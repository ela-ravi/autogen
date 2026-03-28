"""
Video Processing Modules

Contains functions for:
- Generating AI-powered recap suggestions
- Extracting and combining video clips
- Removing audio from videos
"""

import os
import json
from moviepy.editor import VideoFileClip, concatenate_videoclips

# Get the directory where this file is located
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_output_path(relative_path):
    """Convert relative output path to absolute path"""
    return os.path.join(SCRIPT_DIR, relative_path)


def _parse_llm_json(raw: str) -> dict:
    """Strip markdown fences and parse JSON from an LLM response."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def _read_transcript_segments(path: str) -> list[dict]:
    """Load transcript segments from JSON or legacy .txt."""
    if path.endswith(".json"):
        with open(path, "r") as f:
            return json.load(f)
    segments = []
    with open(path, "r") as f:
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
    return segments


def validate_clip_timings(clip_timings: list[dict], video_duration: float | None = None) -> list[dict]:
    """Sanitize and validate LLM-returned clip windows.

    Fixes:
      - Negative / zero-length clips (dropped)
      - end > video_duration (clamped)
      - Overlapping ranges (later clip trimmed)
      - Non-chronological order (sorted)

    Returns the cleaned list; raises ValueError if nothing survives.
    """
    cleaned = []
    for clip in sorted(clip_timings, key=lambda c: c["start"]):
        start = round(float(clip.get("start", 0)), 2)
        end = round(float(clip.get("end", start)), 2)
        if end <= start:
            continue
        if video_duration is not None and start >= video_duration:
            continue
        if video_duration is not None and end > video_duration:
            end = round(video_duration, 2)
        if cleaned:
            prev_end = cleaned[-1]["end"]
            if start < prev_end:
                start = prev_end
            if end <= start:
                continue
        cleaned.append({**clip, "start": start, "end": end})

    if not cleaned:
        raise ValueError("No valid clip timings after validation")
    return cleaned


def generate_recap_suggestions(transcription_file, target_duration=30, output_dir="output/transcriptions", narration_language=None):
    """
    Step 3: Generate AI-powered recap suggestions using two focused LLM calls.

    Call 1 — Clip selection (video-editor mindset): returns clip_timings only.
    Call 2 — Narration (scriptwriter mindset): given the selected clips, writes
             recap_text calibrated to the visual timeline.

    Accepts JSON (preferred) or legacy .txt transcription files.

    Args:
        narration_language: Language for the narration output (e.g. "Tamil").
                            If None, narration is written in the same language as the transcript.

    Returns:
        Path to recap_data.json
    """
    from openai import OpenAI
    import dotenv

    dotenv.load_dotenv()

    print(f"\n{'='*70}")
    print(f"STEP 3: GENERATING AI RECAP SUGGESTIONS")
    print(f"{'='*70}")
    print(f"Input: {transcription_file}")

    segments = _read_transcript_segments(transcription_file)
    if not segments:
        raise ValueError("Transcription file is empty or has no segments")

    transcript_json = json.dumps(segments, indent=2)

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), max_retries=5)
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o")

    narration_word_target = max(35, min(220, round(target_duration * 2.0)))
    narration_word_min = max(25, narration_word_target - 25)
    narration_word_max = min(230, narration_word_target + 30)
    print(f"Target duration: {target_duration}s (narration ~{narration_word_target} words, range {narration_word_min}-{narration_word_max})")

    # ------------------------------------------------------------------
    # CALL 1 — Clip selection
    # ------------------------------------------------------------------
    clip_system = (
        "You are a professional video editor. Your job is to select the most "
        "important clip windows from a timestamped transcript to build a recap "
        "of a specific target duration. Think about coverage, pacing, and "
        "avoiding redundancy. Always respond with valid JSON only."
    )
    clip_prompt = f"""Below is a transcript as a JSON array. Each element has "start" (seconds),
"end" (seconds), and "text" (what was spoken).

{transcript_json}

Select clips for a {target_duration}-second video recap.

RULES:
1. Pick segments with the most important or interesting content first.
2. If meaningful dialogue clips total less than {target_duration}s, add
   supplemental segments (visual transitions, atmospheric moments) to reach
   the target.  Label the reason accordingly.
3. Keep clips in chronological order (sorted by start time).
4. No overlapping ranges. No duplicate timestamps.
5. Sum of (end - start) for all clips must equal EXACTLY {target_duration}s (±2s tolerance).

Return JSON only — no explanation, no markdown fences:
{{
  "clip_timings": [
    {{"start": <float>, "end": <float>, "reason": "<why this clip>"}},
    ...
  ]
}}"""

    tolerance = 2.0
    clip_timings = []
    actual_duration = 0
    max_attempts = 3
    clip_messages = [
        {"role": "system", "content": clip_system},
        {"role": "user", "content": clip_prompt},
    ]

    for attempt in range(1, max_attempts + 1):
        print(f"[Call 1] Selecting clips (attempt {attempt}/{max_attempts})...")
        response = client.chat.completions.create(
            model=model_name,
            messages=clip_messages,
            max_tokens=2000,
        )
        result_text = response.choices[0].message.content or ""
        clip_data = _parse_llm_json(result_text)
        clip_timings = clip_data.get("clip_timings", [])
        actual_duration = sum(c["end"] - c["start"] for c in clip_timings)

        if abs(actual_duration - target_duration) <= tolerance:
            print(f"   Duration OK: {actual_duration:.1f}s (target {target_duration}s)")
            break

        print(f"   Duration mismatch: {actual_duration:.1f}s vs target {target_duration}s — retrying...")
        clip_messages.append({"role": "assistant", "content": result_text})
        clip_messages.append({"role": "user", "content": (
            f"The clips total {actual_duration:.1f}s but the target is {target_duration}s. "
            f"Adjust clips so they total EXACTLY {target_duration}s. Return corrected JSON."
        )})

    if abs(actual_duration - target_duration) > tolerance and actual_duration > 0:
        print(f"   Scaling clips: {actual_duration:.1f}s -> {target_duration}s")
        scale = target_duration / actual_duration
        for clip in clip_timings:
            mid = (clip["start"] + clip["end"]) / 2
            half = ((clip["end"] - clip["start"]) * scale) / 2
            clip["start"] = max(0, round(mid - half, 1))
            clip["end"] = round(mid + half, 1)
        actual_duration = sum(c["end"] - c["start"] for c in clip_timings)
        print(f"   Scaled duration: {actual_duration:.1f}s")

    clip_timings = sorted(clip_timings, key=lambda c: c["start"])
    clip_timings = validate_clip_timings(clip_timings)

    # ------------------------------------------------------------------
    # CALL 2 — Narration
    # ------------------------------------------------------------------
    clip_summary = json.dumps(clip_timings, indent=2)
    lang_label = narration_language or "the same language as the transcript"
    narr_system = (
        "You are a professional scriptwriter for video narrations. You write "
        "tight, speech-ready voiceover copy that matches a given clip timeline. "
        "Always respond with valid JSON only."
    )
    narr_prompt = f"""A {target_duration}-second video recap has been assembled from these clips:

{clip_summary}

The original transcript for context:
{transcript_json}

Write a cohesive voiceover narration for this clip timeline.

RULES:
1. About {narration_word_target} spoken words (stay within {narration_word_min}-{narration_word_max} words).
2. Write the narration ENTIRELY in {lang_label}. Do not mix languages.
3. The narration must feel natural when played over the selected clips in order.
4. Account for transitions between clips — smooth bridges, not abrupt topic jumps.
5. Do not add filler silence or padding instructions — write tight, speech-ready copy only.
6. Never reference transcription quality, errors, or technical issues.

Return JSON only:
{{
  "recap_text": "<your narration in {lang_label}>"
}}"""

    print("[Call 2] Writing narration...")
    narr_response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": narr_system},
            {"role": "user", "content": narr_prompt},
        ],
        max_tokens=1500,
    )
    narr_data = _parse_llm_json(narr_response.choices[0].message.content or "{}")
    recap_text = narr_data.get("recap_text", "")

    # ------------------------------------------------------------------
    # Assemble and save
    # ------------------------------------------------------------------
    recap_data = {
        "recap_text": recap_text,
        "clip_timings": clip_timings,
        "total_duration": round(sum(c["end"] - c["start"] for c in clip_timings), 1),
    }

    output_path = get_output_path(output_dir)
    os.makedirs(output_path, exist_ok=True)

    recap_data_file = os.path.join(output_path, "recap_data.json")
    with open(recap_data_file, "w") as f:
        json.dump(recap_data, f, indent=2)

    recap_text_file = os.path.join(output_path, "recap_text.txt")
    with open(recap_text_file, "w") as f:
        f.write(recap_text)

    clip_count = len(clip_timings)
    total_dur = recap_data["total_duration"]

    print(f"✅ Recap suggestions generated!")
    print(f"   Total clips: {clip_count}")
    print(f"   Total duration: {total_dur}s (target: {target_duration}s)")
    print(f"   Narration words: {len(recap_text.split())}")
    print(f"   Data: {recap_data_file}")
    print(f"   Text: {recap_text_file}")

    return recap_data_file


def extract_and_merge_clips(video_path, recap_data_file, target_duration=30, output_dir="output/videos"):
    """
    Step 4: Extract video clips and merge them
    
    Args:
        video_path: Path to original video
        recap_data_file: Path to recap_data.json
        target_duration: Target duration in seconds (should include overshoot buffer)
        output_dir: Directory to save output video
    
    Returns:
        Path to merged video
    """
    print(f"\n{'='*70}")
    print(f"STEP 4: EXTRACTING AND MERGING VIDEO CLIPS")
    print(f"{'='*70}")
    print(f"Video: {video_path}")
    print(f"Recap data: {recap_data_file}")
    
    # Read recap data
    with open(recap_data_file, "r") as f:
        recap_data = json.load(f)
    
    clip_timings = recap_data.get("clip_timings", [])

    if not clip_timings:
        raise ValueError("No clip timings found in recap_data.json")

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Load original video
    print("Loading video...")
    video = VideoFileClip(video_path)

    # Validate and sanitize clip timings against actual video length
    clip_timings = validate_clip_timings(clip_timings, video_duration=video.duration)
    print(f"Validated {len(clip_timings)} clip(s) against video duration {video.duration:.2f}s")

    # Extract clips
    clips = []
    total_clips_duration = 0

    for i, timing in enumerate(clip_timings, 1):
        start = timing["start"]
        end = timing["end"]
        reason = timing.get("reason", "clip")

        print(f"Extracting clip {i}/{len(clip_timings)}: {start}s-{end}s ({reason})")

        try:
            clip = video.subclip(start, end)
            clips.append(clip)
            total_clips_duration += (end - start)
        except Exception as e:
            print(f"Failed to extract clip {i}: {e}")
    
    # Concatenate clips
    print("Combining clips...")
    final_clip = concatenate_videoclips(clips, method="compose")
    
    # Trim video to target duration. The caller requests clips with an
    # overshoot buffer (+5s) so the video should always be longer than the
    # audio narration — just trim the excess.
    current_duration = final_clip.duration
    print(f"Current duration: {current_duration:.2f}s")
    print(f"Target duration: {target_duration}s")
    
    if current_duration > target_duration + 0.1:
        print(f"Trimming video from {current_duration:.2f}s to {target_duration:.1f}s...")
        final_clip = final_clip.subclip(0, target_duration)
        print(f"✅ Trimmed to {final_clip.duration:.2f}s")
    elif current_duration < target_duration - 0.1:
        print(f"⚠️  Video ({current_duration:.2f}s) is shorter than target ({target_duration}s) — proceeding as-is")
    else:
        print(f"✅ Duration matches target: {current_duration:.2f}s")
    
    print(f"\n✅ Final video duration: {final_clip.duration:.2f}s")
    
    # Save video
    output_path = get_output_path(output_dir)
    os.makedirs(output_path, exist_ok=True)
    
    output_file = os.path.join(output_path, "recap_video.mp4")
    print(f"Writing video to {output_file}...")
    
    # Create temp directory for MoviePy temporary files
    temp_dir = get_output_path("output/temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_audio_file = os.path.join(temp_dir, "temp-audio.m4a")
    
    final_clip.write_videofile(
        output_file,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=temp_audio_file,
        remove_temp=False  # Keep temp file for debugging
    )
    
    print(f"   Temp audio preserved: {temp_audio_file}")
    
    # Clean up
    video.close()
    final_clip.close()
    for clip in clips:
        clip.close()
    
    print(f"✅ Video clips merged!")
    print(f"   Output: {output_file}")
    print(f"   Duration: {target_duration}s")
    
    return output_file


def remove_audio_from_video(input_video, output_video=None):
    """
    Step 5: Remove audio from video
    
    Args:
        input_video: Path to input video
        output_video: Path for output video (optional)
    
    Returns:
        Path to video without audio
    """
    print(f"\n{'='*70}")
    print(f"STEP 5: REMOVING AUDIO FROM VIDEO")
    print(f"{'='*70}")
    print(f"Input: {input_video}")
    
    if not os.path.exists(input_video):
        raise FileNotFoundError(f"Video file not found: {input_video}")
    
    # Generate output path if not provided
    if output_video is None:
        base_name = os.path.splitext(input_video)[0]
        output_video = f"{base_name}_no_audio.mp4"
    
    print("Loading video...")
    video = VideoFileClip(input_video)
    
    print("Removing audio...")
    video_no_audio = video.without_audio()
    
    print(f"Writing output to {output_video}...")
    video_no_audio.write_videofile(
        output_video,
        codec="libx264",
        audio=False,
        logger=None
    )
    
    # Clean up
    video.close()
    video_no_audio.close()
    
    input_size = os.path.getsize(input_video) / (1024 * 1024)
    output_size = os.path.getsize(output_video) / (1024 * 1024)
    
    print(f"✅ Audio removed!")
    print(f"   Output: {output_video}")
    print(f"   Size: {input_size:.2f}MB → {output_size:.2f}MB")
    
    return output_video


__all__ = [
    'generate_recap_suggestions',
    'extract_and_merge_clips',
    'remove_audio_from_video',
    'validate_clip_timings',
    'get_output_path',
]

