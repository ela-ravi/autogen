import os
from contextlib import contextmanager
from typing import Callable


@contextmanager
def patched_module_paths(working_dir: str):
    """Temporarily patch SCRIPT_DIR and get_output_path in modules.transcription."""
    import modules.transcription as mod

    original_script_dir = mod.SCRIPT_DIR
    original_get_output_path = mod.get_output_path

    mod.SCRIPT_DIR = working_dir
    mod.get_output_path = lambda rel: os.path.join(working_dir, rel)
    try:
        yield
    finally:
        mod.SCRIPT_DIR = original_script_dir
        mod.get_output_path = original_get_output_path


def transcribe_video_service(
    video_path: str,
    working_dir: str,
    model_size: str = "small",
    language: str | None = None,
    progress_callback: Callable | None = None,
) -> dict:
    """Wrap modules.transcription.transcribe_video with path isolation."""
    from modules.transcription import transcribe_video

    with patched_module_paths(working_dir):
        if progress_callback:
            progress_callback(step=1, message="Loading Whisper model and transcribing...")
        result_path = transcribe_video(
            video_path,
            output_dir="output/transcriptions",
            model_size=model_size,
            language=language,
        )
        if progress_callback:
            progress_callback(step=1, message="Transcription complete")
        return {"transcription_file": result_path}


def translate_transcription_service(
    transcription_file: str,
    working_dir: str,
    source_lang: str,
    target_lang: str,
    progress_callback: Callable | None = None,
) -> dict:
    """Wrap modules.transcription.translate_transcription with path isolation."""
    from modules.transcription import translate_transcription

    with patched_module_paths(working_dir):
        if progress_callback:
            progress_callback(step=2, message=f"Translating {source_lang} → {target_lang}...")
        result_path = translate_transcription(
            transcription_file,
            source_lang=source_lang,
            target_lang=target_lang,
            output_dir="output/transcriptions",
        )
        if progress_callback:
            progress_callback(step=2, message="Translation complete")
        return {"translated_file": result_path}
