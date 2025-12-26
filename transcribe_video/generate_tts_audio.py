#!/usr/bin/env python3
"""
Text-to-Speech Audio Generator for Recap Videos

This module generates audio narration for recap videos using OpenAI's TTS API.
The generated audio is timed to match the recap video duration.

Features:
- Uses OpenAI's gpt-4o-mini TTS model with Nova voice
- Generates professional narration from recap text
- Adjusts narration to match video duration
- Creates audio file ready to be merged with video
"""

import os
import json
from openai import OpenAI
import dotenv

dotenv.load_dotenv()


def generate_recap_narration_audio(
    recap_text=None,
    output_audio_path="recap_narration.mp3",
    tts_model="tts-1",
    tts_voice="nova"
):
    """
    Generate TTS audio narration for the recap video.
    
    Args:
        recap_text: Text to convert to speech (if None, reads from recap_text.txt)
        output_audio_path: Output path for audio file (default: recap_narration.mp3)
        tts_model: OpenAI TTS model to use (default: tts-1, can use tts-1-hd for higher quality)
        tts_voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
    
    Returns:
        Success message with audio file path and duration
    """
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Get recap text
        if recap_text is None:
            if os.path.exists("recap_text.txt"):
                with open("recap_text.txt", "r") as f:
                    recap_text = f.read().strip()
            else:
                return "Error: No recap text provided and recap_text.txt not found"
        
        if not recap_text:
            return "Error: Recap text is empty"
        
        print(f"Generating audio narration...")
        print(f"Text length: {len(recap_text)} characters")
        print(f"Model: {tts_model}, Voice: {tts_voice}")
        
        # Create narration instruction to make it sound like a video description
        text_to_speak = recap_text
        
        # Generate the speech audio using OpenAI TTS API with streaming response
        with client.audio.speech.with_streaming_response.create(
            model=tts_model,
            voice=tts_voice,
            input=text_to_speak,
            response_format="mp3"
        ) as response:
            # Stream the audio content to the specified file
            response.stream_to_file(output_audio_path)
        
        # Get audio file size
        if os.path.exists(output_audio_path):
            file_size = os.path.getsize(output_audio_path) / 1024  # KB
            
            # Try to get audio duration
            duration_str = "unknown"
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_mp3(output_audio_path)
                duration = len(audio) / 1000.0  # Convert to seconds
                duration_str = f"{duration:.1f}s"
            except ImportError:
                duration_str = "install pydub to check duration"
            except Exception:
                pass
            
            return f"✅ Audio successfully generated and saved as {output_audio_path} ({file_size:.1f} KB, duration: {duration_str})"
        else:
            return "Error: Audio file was not created"
    
    except Exception as e:
        return f"Error generating audio: {str(e)}"


def generate_timed_recap_audio(
    target_duration=30,
    output_audio_path="recap_narration_timed.mp3",
    tts_model="tts-1",
    tts_voice="nova"
):
    """
    Generate TTS audio that matches the recap video duration.
    Adjusts the recap text if needed to fit the target duration.
    
    Args:
        target_duration: Target duration in seconds (default: 30)
        output_audio_path: Output path for audio file
        tts_model: OpenAI TTS model
        tts_voice: Voice to use
    
    Returns:
        Success message with timing information
    """
    try:
        # Get recap data
        if not os.path.exists("recap_data.json"):
            return "Error: recap_data.json not found. Please generate recap first."
        
        with open("recap_data.json", "r") as f:
            recap_data = json.load(f)
        
        recap_text = recap_data.get("recap_text", "")
        video_duration = recap_data.get("total_duration", target_duration)
        
        if not recap_text:
            return "Error: No recap text found in recap_data.json"
        
        print(f"\n{'='*60}")
        print(f"GENERATING TIMED AUDIO NARRATION")
        print(f"{'='*60}")
        print(f"Target video duration: {video_duration}s")
        print(f"Recap text: {recap_text[:100]}...")
        
        # Generate narration with video description context
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # First, generate the audio
        narration_text = f"Here's a quick recap: {recap_text}"
        
        print(f"\nGenerating audio with {tts_model} ({tts_voice} voice)...")
        
        with client.audio.speech.with_streaming_response.create(
            model=tts_model,
            voice=tts_voice,
            input=narration_text,
            response_format="mp3"
        ) as response:
            response.stream_to_file(output_audio_path)
        
        print(f"✅ Audio saved to: {output_audio_path}")
        
        # Check audio duration
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_mp3(output_audio_path)
            audio_duration = len(audio) / 1000.0  # seconds
            
            print(f"\n📊 Timing Analysis:")
            print(f"   Video duration: {video_duration:.1f}s")
            print(f"   Audio duration: {audio_duration:.1f}s")
            
            if abs(audio_duration - video_duration) < 2:
                print(f"   ✅ Perfect timing match!")
            elif audio_duration < video_duration:
                diff = video_duration - audio_duration
                print(f"   ⚠️  Audio is {diff:.1f}s shorter than video")
                print(f"      Tip: Add background music or extend narration")
            else:
                diff = audio_duration - video_duration
                print(f"   ⚠️  Audio is {diff:.1f}s longer than video")
                print(f"      Tip: Speed up audio or shorten text")
            
            return f"Audio generated: {output_audio_path} (Video: {video_duration:.1f}s, Audio: {audio_duration:.1f}s)"
        
        except ImportError:
            print("\n💡 Install pydub for audio duration analysis: pip install pydub")
            return f"Audio generated: {output_audio_path}"
        
    except Exception as e:
        return f"Error generating timed audio: {str(e)}"


def merge_audio_with_video(
    video_path="recap_video.mp4",
    audio_path="recap_narration_timed.mp3",
    output_path="recap_video_with_narration.mp4"
):
    """
    Merge the generated audio narration with the recap video.
    Replaces the original video audio with the narration.
    
    Args:
        video_path: Path to the video file
        audio_path: Path to the audio narration file
        output_path: Output path for the final video
    
    Returns:
        Success message
    """
    try:
        from moviepy.editor import VideoFileClip, AudioFileClip
        
        if not os.path.exists(video_path):
            return f"Error: Video file not found: {video_path}"
        
        if not os.path.exists(audio_path):
            return f"Error: Audio file not found: {audio_path}"
        
        print(f"\n{'='*60}")
        print(f"MERGING AUDIO WITH VIDEO")
        print(f"{'='*60}")
        
        # Load video and audio
        print(f"Loading video: {video_path}...")
        video = VideoFileClip(video_path)
        
        print(f"Loading audio: {audio_path}...")
        audio = AudioFileClip(audio_path)
        
        # Adjust audio to match video duration if needed
        video_duration = video.duration
        audio_duration = audio.duration
        
        print(f"\nDuration comparison:")
        print(f"   Video: {video_duration:.1f}s")
        print(f"   Audio: {audio_duration:.1f}s")
        
        if abs(audio_duration - video_duration) > 0.5:  # More than 0.5s difference
            if audio_duration < video_duration:
                # Audio is shorter - need to slow it down
                print(f"   → Time-stretching audio to match video duration")
                print(f"      Original audio: {audio_duration:.1f}s")
                print(f"      Target duration: {video_duration:.1f}s")
                print(f"      Stretching by: {(video_duration/audio_duration - 1)*100:.1f}%")
                
                # Use fl() to manually time-stretch the audio
                # This works with MoviePy 1.0.3
                time_factor = video_duration / audio_duration
                audio = audio.fl(lambda gf, t: gf(t / time_factor), keep_duration=True)
                audio = audio.set_duration(video_duration)
                
                print(f"      ✅ Audio stretched to: {video_duration:.1f}s")
                
            elif audio_duration > video_duration:
                # Audio is longer - need to speed it up
                print(f"   → Speeding up audio to match video duration")
                print(f"      Original audio: {audio_duration:.1f}s")
                print(f"      Target duration: {video_duration:.1f}s")
                
                time_factor = video_duration / audio_duration
                audio = audio.fl(lambda gf, t: gf(t / time_factor), keep_duration=True)
                audio = audio.set_duration(video_duration)
                
                print(f"      ✅ Audio adjusted to: {video_duration:.1f}s")
        else:
            print(f"   ✅ Audio and video durations match (within 0.5s)!")
        
        # Set the audio of the video
        print(f"\nMerging audio with video...")
        video_with_audio = video.set_audio(audio)
        
        # Write the output
        print(f"Writing output to: {output_path}...")
        video_with_audio.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac"
        )
        
        # Clean up
        video.close()
        audio.close()
        video_with_audio.close()
        
        # Get file size
        output_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
        
        print(f"\n{'='*60}")
        print(f"✅ SUCCESS!")
        print(f"{'='*60}")
        print(f"Final video: {output_path} ({output_size:.2f} MB)")
        
        return f"✅ Video with narration created: {output_path} ({output_size:.2f} MB)"
    
    except Exception as e:
        return f"Error merging audio with video: {str(e)}"


if __name__ == "__main__":
    """
    Standalone mode - generate audio narration for recap
    """
    import sys
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║         RECAP VIDEO - TTS AUDIO NARRATION GENERATOR             ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
Usage:
    python generate_tts_audio.py                  # Generate timed audio for recap
    python generate_tts_audio.py --merge          # Generate audio and merge with video
    python generate_tts_audio.py --custom "text"  # Generate audio from custom text

Options:
    --help      Show this help message
    --merge     Generate audio and merge with recap video
    --custom    Use custom text instead of recap_text.txt

Examples:
    python generate_tts_audio.py
    python generate_tts_audio.py --merge
    python generate_tts_audio.py --custom "This is a test narration"
        """)
        sys.exit(0)
    
    try:
        # Check for merge flag
        if len(sys.argv) > 1 and sys.argv[1] == "--merge":
            print("Mode: Generate audio and merge with video\n")
            result = generate_timed_recap_audio()
            print(f"\n{result}\n")
            
            if "Error" not in result:
                print("\nMerging audio with video...")
                merge_result = merge_audio_with_video()
                print(f"\n{merge_result}\n")
        
        # Check for custom text
        elif len(sys.argv) > 2 and sys.argv[1] == "--custom":
            custom_text = " ".join(sys.argv[2:])
            print(f"Mode: Custom text narration\n")
            result = generate_recap_narration_audio(recap_text=custom_text)
            print(f"\n{result}\n")
        
        # Default: Generate timed audio
        else:
            print("Mode: Generate timed audio narration\n")
            result = generate_timed_recap_audio()
            print(f"\n{result}\n")
            
            if "Error" not in result:
                print("\n💡 Next step: Merge audio with video")
                print("   Run: python generate_tts_audio.py --merge")
                print("   Or use: merge_audio_with_video() in your code\n")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

