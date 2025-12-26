"""
Audio Processing Modules

Contains functions for:
- Generating TTS audio narration
- Merging audio with video
"""

import os
import json
from openai import OpenAI
import dotenv

dotenv.load_dotenv()

# Get the directory where this file is located
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_output_path(relative_path):
    """Convert relative output path to absolute path"""
    return os.path.join(SCRIPT_DIR, relative_path)


def generate_tts_audio(recap_text_file, target_duration=30, output_dir="output/audio", tts_model="tts-1", tts_voice="nova"):
    """
    Step 6: Generate TTS audio narration
    
    Args:
        recap_text_file: Path to recap_text.txt
        target_duration: Target duration in seconds
        output_dir: Directory to save audio
        tts_model: OpenAI TTS model (tts-1 or tts-1-hd)
        tts_voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
    
    Returns:
        Path to generated audio file
    """
    print(f"\n{'='*70}")
    print(f"STEP 6: GENERATING TTS AUDIO NARRATION")
    print(f"{'='*70}")
    print(f"Input: {recap_text_file}")
    print(f"Model: {tts_model}, Voice: {tts_voice}")
    
    # Read recap text
    with open(recap_text_file, "r") as f:
        recap_text = f.read().strip()
    
    if not recap_text:
        raise ValueError("Recap text is empty")
    
    print(f"Text length: {len(recap_text)} characters")
    print(f"Target duration: {target_duration}s")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Prepare output path
    output_path = get_output_path(output_dir)
    os.makedirs(output_path, exist_ok=True)
    
    output_file = os.path.join(output_path, "recap_narration.mp3")
    
    # Generate TTS audio
    print("Generating audio with OpenAI TTS...")
    # #region agent log
    import time
    import json
    with open('/Volumes/Development/Practise/autogen/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"initial","hypothesisId":"D","location":"audio_processing.py:pre_tts","message":"Before TTS generation","data":{"text_length":len(recap_text),"text_preview":recap_text[:100],"target_duration":target_duration},"timestamp":int(time.time()*1000)})+'\n')
    # #endregion
    with client.audio.speech.with_streaming_response.create(
        model=tts_model,
        voice=tts_voice,
        input=recap_text,
        response_format="mp3",
        speed=1.0
    ) as response:
        response.stream_to_file(output_file)
    
    # Get audio duration if pydub is available
    duration_str = "unknown"
    actual_duration = None
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_mp3(output_file)
        duration = len(audio) / 1000.0
        actual_duration = duration
        duration_str = f"{duration:.1f}s"
    except ImportError:
        duration_str = "install pydub to check duration"
    except Exception:
        pass
    
    # #region agent log
    with open('/Volumes/Development/Practise/autogen/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"initial","hypothesisId":"D","location":"audio_processing.py:post_tts","message":"After TTS generation","data":{"actual_duration":actual_duration,"duration_str":duration_str,"file_exists":os.path.exists(output_file)},"timestamp":int(time.time()*1000)})+'\n')
    # #endregion
    
    file_size = os.path.getsize(output_file) / 1024
    
    print(f"✅ Audio generated!")
    print(f"   Output: {output_file}")
    print(f"   Size: {file_size:.1f} KB")
    print(f"   Duration: {duration_str}")
    
    return output_file


def merge_audio_with_video(video_path, audio_path, output_path=None):
    """
    Step 7: Merge audio with video
    
    Args:
        video_path: Path to video file
        audio_path: Path to audio file
        output_path: Path for output video (optional)
    
    Returns:
        Path to final video with audio
    """
    from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips, AudioClip
    import numpy as np
    
    print(f"\n{'='*70}")
    print(f"STEP 7: MERGING AUDIO WITH VIDEO")
    print(f"{'='*70}")
    print(f"Video: {video_path}")
    print(f"Audio: {audio_path}")
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    # Generate output path if not provided
    if output_path is None:
        video_dir = os.path.dirname(video_path)
        output_path = os.path.join(video_dir, "recap_video_with_narration.mp4")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Load video and audio
    print("Loading video...")
    video = VideoFileClip(video_path)
    
    print("Loading audio...")
    audio = AudioFileClip(audio_path)
    
    video_duration = video.duration
    audio_duration = audio.duration
    
    # #region agent log
    import time
    import json
    with open('/Volumes/Development/Practise/autogen/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"initial","hypothesisId":"E","location":"audio_processing.py:pre_merge","message":"Before audio-video merge","data":{"video_duration":video_duration,"audio_duration":audio_duration,"video_path":video_path,"audio_path":audio_path},"timestamp":int(time.time()*1000)})+'\n')
    # #endregion
    
    print(f"\nDuration comparison:")
    print(f"   Video: {video_duration:.1f}s")
    print(f"   Audio: {audio_duration:.1f}s")
    
    # Adjust audio to match video duration
    if abs(audio_duration - video_duration) > 0.1:
        if audio_duration < video_duration:
            gap = video_duration - audio_duration
            print(f"   → Adding {gap:.1f}s of silence to match video")
            
            # Create silence
            def make_frame(t):
                return np.array([0, 0])
            
            silence = AudioClip(make_frame, duration=gap, fps=audio.fps)
            audio = concatenate_audioclips([audio, silence])
            print(f"      ✅ Audio extended to: {audio.duration:.1f}s")
        else:
            print(f"   → Trimming audio to {video_duration:.1f}s")
            audio = audio.subclip(0, video_duration)
            print(f"      ✅ Audio trimmed to: {audio.duration:.1f}s")
    else:
        print(f"   ✅ Audio and video durations match!")
    
    # Set audio to video
    print("\nMerging audio with video...")
    video_with_audio = video.set_audio(audio)
    
    # Create temp directory for MoviePy temporary files
    temp_dir = get_output_path("output/temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_audio_file = os.path.join(temp_dir, "merge-temp-audio.m4a")
    
    # Write output
    print(f"Writing output to {output_path}...")
    video_with_audio.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=temp_audio_file,
        remove_temp=False  # Keep temp file for debugging
    )
    
    print(f"   Temp audio preserved: {temp_audio_file}")
    
    # Clean up
    video.close()
    audio.close()
    video_with_audio.close()
    
    output_size = os.path.getsize(output_path) / (1024 * 1024)
    
    print(f"\n✅ Audio merged with video!")
    print(f"   Output: {output_path}")
    print(f"   Size: {output_size:.2f} MB")
    print(f"   Duration: {video_duration:.1f}s")
    
    return output_path


__all__ = [
    'generate_tts_audio',
    'merge_audio_with_video',
    'get_output_path'
]

