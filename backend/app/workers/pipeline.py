import logging
import os
import shutil
import tempfile
from datetime import datetime, timedelta, timezone

from app.processing.audio_processing import generate_tts_service, merge_audio_video_service
from app.processing.progress import ProgressReporter
from app.processing.transcription import transcribe_video_service, translate_transcription_service
from app.processing.video_processing import extract_clips_service, generate_recap_service, remove_audio_service
from app.services.storage import storage

logger = logging.getLogger(__name__)


class RecapPipeline:
    """Orchestrates the 7-step video recap pipeline with S3 integration."""

    def __init__(self, job_id: str, job_config: dict, input_video_key: str,
                 update_job_fn=None, publish_progress_fn=None):
        self.job_id = job_id
        self.config = job_config
        self.input_video_key = input_video_key
        self.update_job_fn = update_job_fn
        self.working_dir = None

        reporter_callback = publish_progress_fn or (lambda **kw: None)
        self.progress = ProgressReporter(reporter_callback)

    def _setup_working_dir(self) -> str:
        working_dir = tempfile.mkdtemp(prefix=f"recap_{self.job_id}_")
        for subdir in [
            "output/transcriptions",
            "output/videos",
            "output/audio",
            "output/original",
            "output/temp",
        ]:
            os.makedirs(os.path.join(working_dir, subdir), exist_ok=True)
        self.working_dir = working_dir
        return working_dir

    def _progress_callback(self, step: int, message: str):
        self.progress.report(step, message, sub_progress=0.5)

    def _update_job(self, **kwargs):
        if self.update_job_fn:
            self.update_job_fn(self.job_id, **kwargs)

    def run(self):
        working_dir = self._setup_working_dir()
        intermediate_keys = {}

        try:
            # Download input video from S3
            self._update_job(status="processing", current_step=0, current_step_name="Downloading video")
            self.progress.report(0, "Downloading video from storage...", 0.0)
            video_filename = os.path.basename(self.input_video_key)
            local_video_path = os.path.join(working_dir, video_filename)
            storage.download_file(self.input_video_key, local_video_path)

            target_duration = self.config.get("target_duration", 30)
            model_size = self.config.get("whisper_model", "small")
            language = self.config.get("language")
            translate_to = self.config.get("translate_to")
            tts_model = self.config.get("tts_model", "tts-1")
            tts_voice = self.config.get("tts_voice", "nova")
            pad_with_black = self.config.get("pad_with_black", False)

            # Step 1: Transcribe
            self._update_job(current_step=1, current_step_name="Transcribing video")
            self.progress.report(1, "Starting transcription...", 0.0)
            result = transcribe_video_service(
                local_video_path, working_dir,
                model_size=model_size, language=language,
                progress_callback=self._progress_callback,
            )
            transcription_file = result["transcription_file"]
            self._upload_intermediate(intermediate_keys, "transcription", transcription_file)
            self.progress.report(1, "Transcription complete", 1.0)

            # Step 2: Translate (optional)
            active_transcription = transcription_file
            if translate_to:
                self._update_job(current_step=2, current_step_name="Translating")
                self.progress.report(2, "Starting translation...", 0.0)
                source_lang = language or "en"
                result = translate_transcription_service(
                    transcription_file, working_dir,
                    source_lang=source_lang, target_lang=translate_to,
                    progress_callback=self._progress_callback,
                )
                active_transcription = result["translated_file"]
                self._upload_intermediate(intermediate_keys, "translation", active_transcription)
                self.progress.report(2, "Translation complete", 1.0)
            else:
                self.progress.report(2, "Translation skipped", 1.0)

            # Step 3: Generate recap
            self._update_job(current_step=3, current_step_name="Generating recap")
            self.progress.report(3, "Generating recap suggestions...", 0.0)
            result = generate_recap_service(
                active_transcription, working_dir,
                target_duration=target_duration,
                progress_callback=self._progress_callback,
            )
            recap_data_file = result["recap_data_file"]
            self._upload_intermediate(intermediate_keys, "recap_data", recap_data_file)
            self.progress.report(3, "Recap generated", 1.0)

            # Step 4: Generate TTS (moved before clip extraction to determine actual audio duration)
            recap_text_file = os.path.join(working_dir, "output/transcriptions/recap_text.txt")
            self._update_job(current_step=4, current_step_name="Generating narration")
            self.progress.report(4, "Generating TTS narration...", 0.0)
            result = generate_tts_service(
                recap_text_file, working_dir,
                target_duration=target_duration,
                tts_model=tts_model, voice=tts_voice,
                progress_callback=self._progress_callback,
            )
            tts_audio_file = result["tts_audio_file"]
            actual_audio_duration = result["actual_audio_duration"]
            self._upload_intermediate(intermediate_keys, "tts_audio", tts_audio_file)
            self.progress.report(4, f"TTS narration ready ({actual_audio_duration:.1f}s)", 1.0)

            # Step 5: Extract clips (use audio duration so video >= audio)
            self._update_job(current_step=5, current_step_name="Extracting clips")
            self.progress.report(5, "Extracting video clips...", 0.0)
            result = extract_clips_service(
                local_video_path, recap_data_file, working_dir,
                target_duration=actual_audio_duration,
                pad_with_black=True,
                progress_callback=self._progress_callback,
            )
            recap_video_file = result["recap_video_file"]
            self._upload_intermediate(intermediate_keys, "recap_video", recap_video_file)
            self.progress.report(5, "Clips extracted", 1.0)

            # Step 6: Remove audio
            self._update_job(current_step=6, current_step_name="Removing audio")
            self.progress.report(6, "Removing original audio...", 0.0)
            result = remove_audio_service(
                recap_video_file, working_dir,
                progress_callback=self._progress_callback,
            )
            no_audio_video = result["no_audio_video_file"]
            self.progress.report(6, "Audio removed", 1.0)

            # Step 7: Merge audio + video
            self._update_job(current_step=7, current_step_name="Merging final video")
            self.progress.report(7, "Merging audio with video...", 0.0)
            result = merge_audio_video_service(
                no_audio_video, tts_audio_file, working_dir,
                progress_callback=self._progress_callback,
            )
            final_video = result["final_video_file"]
            self.progress.report(7, "Final video ready", 1.0)

            # Upload final output to S3
            output_key = f"results/{self.job_id}/recap_video_with_narration.mp4"
            with open(final_video, "rb") as f:
                storage.upload_file(output_key, f)

            # Calculate expiry based on tier (default 7 days for free)
            expires_at = datetime.now(timezone.utc) + timedelta(days=7)

            self._update_job(
                status="completed",
                current_step=7,
                current_step_name="Complete",
                progress_pct=100.0,
                output_video_key=output_key,
                intermediate_keys=intermediate_keys,
                completed_at=datetime.now(timezone.utc),
                expires_at=expires_at,
            )

            return {"output_key": output_key, "intermediate_keys": intermediate_keys}

        except Exception as e:
            logger.exception(f"Pipeline failed for job {self.job_id}")
            self._update_job(
                status="failed",
                error_message=str(e),
            )
            raise
        finally:
            if self.working_dir and os.path.exists(self.working_dir):
                shutil.rmtree(self.working_dir, ignore_errors=True)

    def _upload_intermediate(self, keys_dict: dict, name: str, local_path: str):
        if not os.path.exists(local_path):
            return
        s3_key = f"jobs/{self.job_id}/{name}/{os.path.basename(local_path)}"
        with open(local_path, "rb") as f:
            storage.upload_file(s3_key, f)
        keys_dict[name] = s3_key
