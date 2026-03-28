"""
Modular Video Transcription and Recap Generation

This module contains individual functions for each step of the workflow.
Each function is independent and can be called separately.
"""

import json
import os
import threading
from typing import Any

import whisper
from moviepy.editor import VideoFileClip

# Get the directory where this file is located (parent of modules/)
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# One Whisper model per (model_size) per process — Celery workers reuse the same process,
# so the second+ job avoids disk load and model init latency.
_WHISPER_MODEL_CACHE: dict[str, Any] = {}
_WHISPER_LOAD_LOCK = threading.Lock()
# Last Redis "generation" this process applied (see sync_whisper_cache_invalidation).
_WHISPER_GEN_SEEN: int = -1

# Redis key for global cache bust (INCR from API); workers observe on next transcribe.
WHISPER_CACHE_REDIS_KEY = "videorecap:whisper_cache_gen"


def is_whisper_model_cached(model_size: str) -> bool:
    return model_size in _WHISPER_MODEL_CACHE


def _get_whisper_model(model_size: str):
    if model_size not in _WHISPER_MODEL_CACHE:
        with _WHISPER_LOAD_LOCK:
            if model_size not in _WHISPER_MODEL_CACHE:
                print(f"Loading Whisper model '{model_size}' (cached for reuse in this worker)...")
                _WHISPER_MODEL_CACHE[model_size] = whisper.load_model(model_size)
    else:
        print(f"Using cached Whisper model '{model_size}' (no reload)")
    return _WHISPER_MODEL_CACHE[model_size]


def clear_whisper_model_cache() -> None:
    """Remove loaded Whisper models from this process (next job loads from disk again)."""
    global _WHISPER_MODEL_CACHE
    with _WHISPER_LOAD_LOCK:
        _WHISPER_MODEL_CACHE.clear()
    print("Whisper in-process cache cleared for this worker.")


def sync_whisper_cache_invalidation(redis_url: str | None) -> None:
    """If Redis generation changed (user requested cache clear), drop local Whisper cache."""
    global _WHISPER_GEN_SEEN
    if not redis_url:
        return
    try:
        import redis as redis_sync

        r = redis_sync.Redis.from_url(redis_url, decode_responses=True)
        try:
            raw = r.get(WHISPER_CACHE_REDIS_KEY)
            gen = int(raw) if raw is not None else 0
        finally:
            r.close()
    except Exception as exc:
        print(f"Whisper cache generation check skipped: {exc}")
        return

    if gen != _WHISPER_GEN_SEEN:
        if _WHISPER_MODEL_CACHE:
            clear_whisper_model_cache()
        _WHISPER_GEN_SEEN = gen


def get_output_path(relative_path):
    """Convert relative output path to absolute path"""
    return os.path.join(SCRIPT_DIR, relative_path)


def transcribe_video(video_path, output_dir="output/transcriptions", model_size="small", language=None):
    """
    Step 1: Transcribe video to text with timestamps
    
    Args:
        video_path: Path to input video file
        output_dir: Directory to save transcription
        model_size: Whisper model size (tiny, base, small, medium, large)
        language: Language code (e.g., 'en' for English, 'es' for Spanish). Auto-detect if None.
    
    Returns:
        Path to transcription file
    """
    print(f"\n{'='*70}")
    print(f"STEP 1: TRANSCRIBING VIDEO")
    print(f"{'='*70}")
    print(f"Video: {video_path}")
    print(f"Model: {model_size}")
    if language:
        print(f"Language: {language}")
    
    model = _get_whisper_model(model_size)
    
    # Create output directories
    output_path = get_output_path(output_dir)
    os.makedirs(output_path, exist_ok=True)
    
    original_dir = get_output_path("output/original")
    os.makedirs(original_dir, exist_ok=True)
    
    # Extract audio from video
    print("Extracting audio from video...")
    video = VideoFileClip(video_path)
    temp_audio = os.path.join(original_dir, "extracted_audio.wav")
    video.audio.write_audiofile(temp_audio, verbose=False, logger=None)
    video.close()
    
    print(f"Audio extracted to: {temp_audio}")
    
    # Transcribe audio
    print("Transcribing audio...")
    transcribe_options = {"verbose": True}
    if language:
        transcribe_options["language"] = language
    result = model.transcribe(temp_audio, **transcribe_options)
    
    # Process segments
    transcript_data = []
    for segment in result['segments']:
        transcript_data.append({
            "start": segment['start'],
            "end": segment['end'],
            "text": segment['text'].strip()
        })
    
    # Save transcription
    output_path = get_output_path(output_dir)
    os.makedirs(output_path, exist_ok=True)
    
    # Save as JSON
    json_file = os.path.join(output_path, "transcription.json")
    with open(json_file, "w") as f:
        json.dump(transcript_data, f, indent=2)
    
    # Save as human-readable text
    txt_file = os.path.join(output_path, "transcription.txt")
    with open(txt_file, "w") as f:
        for segment in transcript_data:
            f.write(f"{segment['start']:.2f}s to {segment['end']:.2f}s: {segment['text']}\n")
    
    # Save full transcription text to original folder
    full_text_file = os.path.join(original_dir, "full_transcription.txt")
    with open(full_text_file, "w") as f:
        for segment in transcript_data:
            f.write(f"{segment['text']}\n")
    
    print(f"✅ Transcription complete!")
    print(f"   Segments: {len(transcript_data)}")
    print(f"   JSON: {json_file}")
    print(f"   Text: {txt_file}")
    print(f"   Full text: {full_text_file}")
    print(f"   Extracted audio: {temp_audio} (preserved)")
    
    return json_file


def translate_transcription(input_file, source_lang, target_lang, output_dir="output/transcriptions"):
    """
    Step 2: Translate transcription to another language.

    Accepts either a JSON file (list of {start, end, text}) or a legacy .txt
    file.  Always returns a JSON file so downstream consumers get structured data.

    Args:
        input_file: Path to transcription.json (preferred) or .txt
        source_lang: Source language (e.g., "English")
        target_lang: Target language (e.g., "Tamil")
        output_dir: Directory to save translation

    Returns:
        Path to translated JSON file
    """
    from openai import OpenAI
    import dotenv

    dotenv.load_dotenv()

    print(f"\n{'='*70}")
    print(f"STEP 2: TRANSLATING TRANSCRIPTION")
    print(f"{'='*70}")
    print(f"Input: {input_file}")
    print(f"Translation: {source_lang} → {target_lang}")

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Read segments — support both JSON and legacy .txt
    if input_file.endswith(".json"):
        with open(input_file, "r") as f:
            segments = json.load(f)
    else:
        segments = []
        with open(input_file, "r") as f:
            for line in f:
                parts = line.strip().split(": ", 1)
                if len(parts) == 2:
                    ts, text = parts
                    ts_parts = ts.replace("s", "").split(" to ")
                    try:
                        segments.append({
                            "start": float(ts_parts[0]),
                            "end": float(ts_parts[1]),
                            "text": text,
                        })
                    except (ValueError, IndexError):
                        continue

    # Translate each segment's text
    for i, seg in enumerate(segments, 1):
        print(f"Translating segment {i}/{len(segments)}...", end="\r")
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=[
                {"role": "system", "content": "You are a professional translator."},
                {"role": "user", "content": f"Translate this {source_lang} text to {target_lang}: {seg['text']}"},
            ],
            max_tokens=500,
        )
        seg["text"] = response.choices[0].message.content if response.choices else seg["text"]

    print()  # newline after progress

    # Save as JSON
    output_path = get_output_path(output_dir)
    os.makedirs(output_path, exist_ok=True)

    output_file = os.path.join(output_path, f"{target_lang.lower()}_transcription.json")
    with open(output_file, "w") as f:
        json.dump(segments, f, indent=2)

    print(f"✅ Translation complete!")
    print(f"   Segments translated: {len(segments)}")
    print(f"   Output: {output_file}")

    return output_file


# Export functions
__all__ = [
    "WHISPER_CACHE_REDIS_KEY",
    "clear_whisper_model_cache",
    "get_output_path",
    "is_whisper_model_cached",
    "sync_whisper_cache_invalidation",
    "transcribe_video",
    "translate_transcription",
]

