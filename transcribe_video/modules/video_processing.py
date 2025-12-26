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
    
    prompt = f"""You are given a noisy video transcription that contains a mix of English dialogue, names, timestamps, symbols, non-English scripts, and gibberish words.

Transcription:
{transcript_content}

Instructions:

1. Treat all non-English words, symbols, random syllables, numbers, and unclear phrases as background sounds or music and ignore them completely.

2. Extract and consider only clear, meaningful English words and sentences that contribute to dialogue or narrative.

3. Combine the meaningful English content to understand the overall context and story of the video.

4. Based on that understanding, generate a recap narration script suitable for voiceover.

5. The narration must be written in natural, fluent English, with a cohesive beginning, middle, and end.

6. The narration must be timed for {target_duration} seconds of audio, targeting 75–80 words total (do not exceed 80 words).

7. Do not mention transcription errors, missing words, or gibberish in the final output.

8. Select specific clip timings from the original video based on timestamps where meaningful English dialogue appears. The clips should total EXACTLY {target_duration} seconds.

Output format:
Provide your response as JSON:
{{
    "recap_text": "Your natural, fluent English narration here (75-80 words, no explanations)",
    "clip_timings": [
        {{"start": 0, "end": 5, "reason": "Opening dialogue"}},
        {{"start": 19, "end": 22, "reason": "Key moment"}},
        ...
    ],
    "total_duration": {target_duration}
}}

CRITICAL REQUIREMENTS:
- The sum of all clip durations (end - start) MUST equal EXACTLY {target_duration} seconds
- Only include clips where meaningful English dialogue is present
- Ensure clips flow naturally when combined
- The recap_text must be voiceover-ready and exactly 75-80 words
"""
    
    print("Analyzing transcript with AI...")
    response = client.chat.completions.create(
        model=os.getenv("model", "gpt-4"),
        messages=[
            {"role": "system", "content": "You are a professional video editor and content analyst skilled at extracting meaningful content from noisy transcriptions. You excel at filtering out gibberish and focusing on actual dialogue to create engaging recaps. Always respond with valid JSON."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000
    )
    
    result_text = response.choices[0].message.content if response.choices else None
    
    # Parse JSON from response
    if result_text.startswith("```"):
        result_text = result_text.split("```")[1]
        if result_text.startswith("json"):
            result_text = result_text[4:]
    
    recap_data = json.loads(result_text.strip())
    
    # #region agent log
    import time
    clip_durations = [(c.get('end',0) - c.get('start',0)) for c in recap_data.get('clip_timings',[])]
    total_clip_duration = sum(clip_durations)
    with open('/Volumes/Development/Practise/autogen/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"initial","hypothesisId":"A","location":"video_processing.py:180","message":"AI generated clip timings","data":{"clip_count":len(recap_data.get('clip_timings',[])),"clip_durations":clip_durations,"total_duration":total_clip_duration,"target_duration":target_duration},"timestamp":int(time.time()*1000)})+'\n')
    # #endregion
    
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
    total_duration = recap_data.get("total_duration", 0)
    
    print(f"✅ Recap suggestions generated!")
    print(f"   Clips suggested: {clip_count}")
    print(f"   Total duration: {total_duration}s")
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
    # #region agent log
    import time
    extraction_log = []
    # #endregion
    for i, timing in enumerate(clip_timings, 1):
        start = timing.get("start", 0)
        end = timing.get("end", start + 1)
        reason = timing.get("reason", "clip")
        
        print(f"Extracting clip {i}/{len(clip_timings)}: {start}s-{end}s ({reason})")
        
        # #region agent log
        try:
            # #endregion
            clip = video.subclip(start, end)
            clips.append(clip)
            clip_duration = (end - start)
            total_clips_duration += clip_duration
            # #region agent log
            extraction_log.append({"clip_num":i,"start":start,"end":end,"duration":clip_duration,"success":True})
        except Exception as e:
            extraction_log.append({"clip_num":i,"start":start,"end":end,"error":str(e),"success":False})
            print(f"Failed to extract clip {i}: {e}")
    
    with open('/Volumes/Development/Practise/autogen/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"initial","hypothesisId":"B","location":"video_processing.py:197","message":"Clip extraction complete","data":{"total_clips_attempted":len(clip_timings),"successful_clips":len(clips),"total_duration":total_clips_duration,"extraction_details":extraction_log},"timestamp":int(time.time()*1000)})+'\n')
    # #endregion
    
    # Concatenate clips
    print("Combining clips...")
    final_clip = concatenate_videoclips(clips, method="compose")
    
    # #region agent log
    concat_duration = final_clip.duration if hasattr(final_clip, 'duration') else 0
    with open('/Volumes/Development/Practise/autogen/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"initial","hypothesisId":"C","location":"video_processing.py:223","message":"After concatenation","data":{"concatenated_duration":concat_duration,"num_clips":len(clips),"target_duration":target_duration},"timestamp":int(time.time()*1000)})+'\n')
    # #endregion
    
    # Adjust to exactly target_duration
    current_duration = final_clip.duration
    print(f"Current duration: {current_duration:.2f}s")
    print(f"Target duration: {target_duration}s")
    
    if abs(current_duration - target_duration) > 0.1:
        if current_duration < target_duration:
            if pad_with_black:
                gap = target_duration - current_duration
                print(f"Adding {gap:.2f}s of black frames...")
                
                black_clip = ColorClip(
                    size=final_clip.size,
                    color=(0, 0, 0),
                    duration=gap
                )
                final_clip = concatenate_videoclips([final_clip, black_clip], method="compose")
                print(f"✅ Padded to exactly {target_duration} seconds")
            else:
                print(f"⚠️  Video is {current_duration:.2f}s (shorter than target {target_duration}s)")
                print(f"   Skipping black frame padding (use --pad-with-black to enable)")
        elif current_duration > target_duration:
            print(f"Trimming to {target_duration}s...")
            final_clip = final_clip.subclip(0, target_duration)
            print(f"✅ Trimmed to exactly {target_duration} seconds")
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

