import os
from contextlib import contextmanager
from typing import Callable


@contextmanager
def patched_module_paths(working_dir: str):
    """Temporarily patch SCRIPT_DIR and get_output_path in modules.audio_processing."""
    import modules.audio_processing as mod

    original_script_dir = mod.SCRIPT_DIR
    original_get_output_path = mod.get_output_path

    mod.SCRIPT_DIR = working_dir
    mod.get_output_path = lambda rel: os.path.join(working_dir, rel)
    try:
        yield
    finally:
        mod.SCRIPT_DIR = original_script_dir
        mod.get_output_path = original_get_output_path


def generate_tts_service(
    recap_text_file: str,
    working_dir: str,
    target_duration: int = 30,
    tts_model: str = "tts-1",
    voice: str = "nova",
    progress_callback: Callable | None = None,
) -> dict:
    """Wrap modules.audio_processing.generate_tts_audio."""
    from modules.audio_processing import generate_tts_audio

    with patched_module_paths(working_dir):
        if progress_callback:
            progress_callback(step=6, message="Generating TTS narration...")
        result_path = generate_tts_audio(
            recap_text_file,
            target_duration=target_duration,
            output_dir="output/audio",
            tts_model=tts_model,
            tts_voice=voice,
        )
        if progress_callback:
            progress_callback(step=6, message="TTS narration generated")
        return {"tts_audio_file": result_path}


def merge_audio_video_service(
    video_path: str,
    audio_path: str,
    working_dir: str,
    progress_callback: Callable | None = None,
) -> dict:
    """Wrap modules.audio_processing.merge_audio_with_video."""
    from modules.audio_processing import merge_audio_with_video

    with patched_module_paths(working_dir):
        if progress_callback:
            progress_callback(step=7, message="Merging audio with video...")
        result_path = merge_audio_with_video(video_path, audio_path)
        if progress_callback:
            progress_callback(step=7, message="Final video ready")
        return {"final_video_file": result_path}
