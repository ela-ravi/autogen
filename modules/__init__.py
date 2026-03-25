"""
Modular Video Transcription and Recap Generation

This package contains modular functions for video processing workflows.

Modules:
- transcription: Video transcription and translation
- video_processing: Recap generation, clip extraction, audio removal
- audio_processing: TTS generation and audio-video merging
"""

from .transcription import transcribe_video, translate_transcription
from .video_processing import generate_recap_suggestions, extract_and_merge_clips, remove_audio_from_video
from .audio_processing import generate_tts_audio, merge_audio_with_video

__all__ = [
    'transcribe_video',
    'translate_transcription',
    'generate_recap_suggestions',
    'extract_and_merge_clips',
    'remove_audio_from_video',
    'generate_tts_audio',
    'merge_audio_with_video'
]

