"""
Video Processing Modules

Contains functions for:
- Generating AI-powered recap suggestions
- Extracting and combining video clips
- Removing audio from videos
"""

import os
import json
from moviepy.editor import VideoFileClip, concatenate_videoclips, ColorClip

# Get the directory where this file is located
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_output_path(relative_path):
    """Convert relative output path to absolute path"""
    return os.path.join(SCRIPT_DIR, relative_path)


def generate_recap_suggestions(transcription_file, target_duration=30, output_dir="output/transcriptions"):
    """
    Step 3: Generate AI-powered recap suggestions
    
    Args:
        transcription_file: Path to transcription.txt
        target_duration: Target duration for recap in seconds
        output_dir: Directory to save recap data
    
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
    print(f"Target duration: {target_duration}s")
    
    # Read transcription
    with open(transcription_file, "r") as f:
        transcript_content = f.read()
    
    if not transcript_content.strip():
        raise ValueError("Transcription file is empty")
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = f"""You are a professional video editor analyzing a noisy video transcription that contains meaningful English dialogue mixed with gibberish, symbols, non-English text, and background sounds.

Transcription:
{transcript_content}

YOUR TASK: Create a {target_duration}-second video recap using a TWO-PASS clip selection approach.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PASS 1: PRIMARY CLIPS (Meaningful Dialogue)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Identify segments with clear, meaningful English dialogue
2. Extract timestamps for these dialogue-driven moments
3. Calculate total duration of these clips

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PASS 2: SUPPLEMENTAL CLIPS (Fill to {target_duration} seconds)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IF primary clips total < {target_duration} seconds:
1. Identify segments with gibberish/sounds/non-English (unused timestamps)
2. Select these as "atmospheric" or "transitional" clips
3. Insert them in CHRONOLOGICAL ORDER (not at the end)
4. Label them as: "Atmospheric moment", "Visual transition", "Emotional buildup", etc.
5. Continue until total = EXACTLY {target_duration} seconds

IMPORTANT: 
- Keep all clips in chronological order by timestamp
- Do NOT duplicate any timestamps
- Supplemental clips should fit naturally between dialogue clips

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NARRATION GENERATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Based on the FULL clip timeline (dialogue + atmospheric):
1. Write a natural, cohesive narration (75-80 words)
2. Account for atmospheric clips as transitions, mood, or buildup
3. Create smooth narrative flow across all clips
4. Time for {target_duration} seconds of voiceover
5. Never mention "gibberish", "errors", or transcription issues

Example narration flow:
"[Dialogue moment] ... [transition acknowledging atmosphere] ... [next dialogue moment]"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Provide your response as JSON:
{{
    "recap_text": "Your natural narration (75-80 words, accounts for all clips)",
    "clip_timings": [
        {{"start": 0, "end": 5, "reason": "Opening dialogue", "type": "dialogue"}},
        {{"start": 10, "end": 13, "reason": "Visual transition", "type": "atmospheric"}},
        {{"start": 19, "end": 22, "reason": "Key moment", "type": "dialogue"}},
        ...
    ],
    "total_duration": {target_duration}
}}

CRITICAL VALIDATION CHECKLIST:
✓ Sum of (end - start) for ALL clips = EXACTLY {target_duration} seconds
✓ Clips are in chronological order (sorted by start time)
✓ No duplicate timestamps
✓ Narration is 75-80 words
✓ Narration accounts for atmospheric clips smoothly
✓ Mix of "dialogue" and "atmospheric" clips if needed

REJECT if:
✗ Total duration ≠ {target_duration} seconds
✗ Only dialogue clips and total < {target_duration} seconds (MUST add atmospheric clips)
✗ Clips out of chronological order
"""
    
    system_msg = "You are a professional video editor skilled at creating engaging recaps from noisy transcriptions. You use a TWO-PASS approach: (1) Select dialogue clips first, (2) Fill remaining duration with atmospheric/transition clips from non-dialogue segments. You ALWAYS ensure clips total EXACTLY the target duration by using both dialogue and atmospheric moments. You maintain chronological order and create smooth, natural narrations that account for all clip types. Always respond with valid JSON."
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": prompt}
    ]
    
    tolerance = 2.0
    recap_data = None
    actual_duration = 0
    max_attempts = 3
    
    for attempt in range(1, max_attempts + 1):
        print(f"Analyzing transcript with AI (attempt {attempt}/{max_attempts})...")
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            messages=messages,
            max_tokens=2500
        )
        
        result_text = response.choices[0].message.content if response.choices else None
        
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        
        recap_data = json.loads(result_text.strip())
        clip_timings = recap_data.get('clip_timings', [])
        actual_duration = sum(clip['end'] - clip['start'] for clip in clip_timings)
        
        if abs(actual_duration - target_duration) <= tolerance:
            print(f"   Duration OK: {actual_duration:.1f}s (target {target_duration}s)")
            break
        
        print(f"   Duration mismatch: {actual_duration:.1f}s vs target {target_duration}s — retrying...")
        messages.append({"role": "assistant", "content": response.choices[0].message.content})
        messages.append({"role": "user", "content": (
            f"The clips you selected total {actual_duration:.1f} seconds, but the target is "
            f"EXACTLY {target_duration} seconds. You are off by "
            f"{target_duration - actual_duration:.1f}s. Please add more clips to fill the gap. "
            f"Return the complete corrected JSON with all clips."
        )})
    
    if abs(actual_duration - target_duration) > tolerance and actual_duration > 0:
        print(f"   Scaling clips: {actual_duration:.1f}s -> {target_duration}s")
        scale = target_duration / actual_duration
        clip_timings = recap_data.get('clip_timings', [])
        for clip in clip_timings:
            mid = (clip['start'] + clip['end']) / 2
            half = ((clip['end'] - clip['start']) * scale) / 2
            clip['start'] = max(0, round(mid - half, 1))
            clip['end'] = round(mid + half, 1)
        recap_data['clip_timings'] = clip_timings
        actual_duration = sum(c['end'] - c['start'] for c in clip_timings)
        print(f"   Scaled duration: {actual_duration:.1f}s")
    
    # Sort clips by start time to ensure chronological order
    recap_data['clip_timings'] = sorted(clip_timings, key=lambda x: x['start'])
    
    # Save recap data
    output_path = get_output_path(output_dir)
    os.makedirs(output_path, exist_ok=True)
    
    recap_data_file = os.path.join(output_path, "recap_data.json")
    with open(recap_data_file, "w") as f:
        json.dump(recap_data, f, indent=2)
    
    # Save recap text separately
    recap_text_file = os.path.join(output_path, "recap_text.txt")
    with open(recap_text_file, "w") as f:
        f.write(recap_data.get("recap_text", ""))
    
    clip_count = len(recap_data.get("clip_timings", []))
    dialogue_count = len([c for c in recap_data.get("clip_timings", []) if c.get('type') == 'dialogue'])
    atmospheric_count = len([c for c in recap_data.get("clip_timings", []) if c.get('type') == 'atmospheric'])
    total_duration = recap_data.get("total_duration", 0)
    
    print(f"✅ Recap suggestions generated!")
    print(f"   Total clips: {clip_count} ({dialogue_count} dialogue + {atmospheric_count} atmospheric)")
    print(f"   Total duration: {total_duration}s (target: {target_duration}s)")
    print(f"   Data: {recap_data_file}")
    print(f"   Text: {recap_text_file}")
    
    return recap_data_file


def extract_and_merge_clips(video_path, recap_data_file, target_duration=30, output_dir="output/videos", pad_with_black=False):
    """
    Step 4: Extract video clips and merge them
    
    Args:
        video_path: Path to original video
        recap_data_file: Path to recap_data.json
        target_duration: Target duration in seconds
        output_dir: Directory to save output video
        pad_with_black: Whether to pad with black frames if video is shorter (default: False)
    
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
    
    # Extract clips
    clips = []
    total_clips_duration = 0
    
    for i, timing in enumerate(clip_timings, 1):
        start = timing.get("start", 0)
        end = timing.get("end", start + 1)
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
    
    # Ensure video is at least as long as target_duration (audio duration).
    # If shorter, pad with black frames. If longer, trim to match.
    current_duration = final_clip.duration
    print(f"Current duration: {current_duration:.2f}s")
    print(f"Target duration (audio): {target_duration}s")
    
    if current_duration < target_duration - 0.1:
        gap = target_duration - current_duration
        print(f"Video shorter than audio — padding with {gap:.2f}s of black frames...")
        black_clip = ColorClip(
            size=final_clip.size,
            color=(0, 0, 0),
            duration=gap
        )
        final_clip = concatenate_videoclips([final_clip, black_clip], method="compose")
        print(f"✅ Padded to {final_clip.duration:.2f}s")
    elif current_duration > target_duration + 0.1:
        print(f"Trimming video from {current_duration:.2f}s to {target_duration:.1f}s...")
        final_clip = final_clip.subclip(0, target_duration)
        print(f"✅ Trimmed to {final_clip.duration:.2f}s")
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
    'get_output_path'
]

