import os
from contextlib import contextmanager
from typing import Callable


@contextmanager
def patched_module_paths(working_dir: str):
    """Temporarily patch SCRIPT_DIR and get_output_path in modules.video_processing."""
    import modules.video_processing as mod

    original_script_dir = mod.SCRIPT_DIR
    original_get_output_path = mod.get_output_path

    mod.SCRIPT_DIR = working_dir
    mod.get_output_path = lambda rel: os.path.join(working_dir, rel)
    try:
        yield
    finally:
        mod.SCRIPT_DIR = original_script_dir
        mod.get_output_path = original_get_output_path


def generate_recap_service(
    transcription_file: str,
    working_dir: str,
    target_duration: int = 30,
    narration_language: str | None = None,
    progress_callback: Callable | None = None,
) -> dict:
    """Wrap modules.video_processing.generate_recap_suggestions."""
    from modules.video_processing import generate_recap_suggestions

    with patched_module_paths(working_dir):
        if progress_callback:
            progress_callback(step=3, message="AI analyzing transcription for recap...")
        result_path = generate_recap_suggestions(
            transcription_file,
            target_duration=target_duration,
            output_dir="output/transcriptions",
            narration_language=narration_language,
        )
        if progress_callback:
            progress_callback(step=3, message="Recap suggestions generated")
        return {"recap_data_file": result_path}


def extract_clips_service(
    video_path: str,
    recap_data_file: str,
    working_dir: str,
    target_duration: float = 30,
    progress_callback: Callable | None = None,
) -> dict:
    """Wrap modules.video_processing.extract_and_merge_clips."""
    from modules.video_processing import extract_and_merge_clips

    with patched_module_paths(working_dir):
        if progress_callback:
            progress_callback(step=5, message="Extracting and merging video clips...")
        result_path = extract_and_merge_clips(
            video_path,
            recap_data_file,
            target_duration=target_duration,
            output_dir="output/videos",
        )
        if progress_callback:
            progress_callback(step=5, message="Clips extracted and merged")
        return {"recap_video_file": result_path}


def remove_audio_service(
    video_path: str,
    working_dir: str,
    progress_callback: Callable | None = None,
) -> dict:
    """Wrap modules.video_processing.remove_audio_from_video."""
    from modules.video_processing import remove_audio_from_video

    with patched_module_paths(working_dir):
        if progress_callback:
            progress_callback(step=6, message="Removing original audio...")
        result_path = remove_audio_from_video(video_path)
        if progress_callback:
            progress_callback(step=6, message="Audio removed")
        return {"no_audio_video_file": result_path}
