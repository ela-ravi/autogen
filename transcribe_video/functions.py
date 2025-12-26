import os
import json
import dotenv
import whisper
from openai import OpenAI
from moviepy.editor import VideoFileClip

dotenv.load_dotenv()

# Get the directory where this functions.py file is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Helper function to get absolute paths relative to script directory
def get_output_path(relative_path):
    """Convert relative output path to absolute path"""
    return os.path.join(SCRIPT_DIR, relative_path)


def recognize_transcript_from_video(audio_filepath):
    try:
        # Load model
        model = whisper.load_model("small")

        # Transcribe audio with detailed timestamps
        result = model.transcribe(audio_filepath, verbose=True)

        # Initialize variables for transcript
        transcript = []
        sentence = ""
        start_time = 0

        # Iterate through the segments in the result
        for segment in result['segments']:
            # If new sentence starts, save the previous one and reset variables
            if segment['start'] != start_time and sentence:
                transcript.append({
                    "sentence": sentence.strip() + ".",
                    "timestamp_start": start_time,
                    "timestamp_end": segment['start']
                })
                sentence = ""
                start_time = segment['start']

            # Add the word to the current sentence
            sentence += segment['text'] + " "

        # Add the final sentence
        if sentence:
            transcript.append({
                "sentence": sentence.strip() + ".",
                "timestamp_start": start_time,
                "timestamp_end": result['segments'][-1]['end']
            })

        # Save the transcript to a file
        output_dir = get_output_path("output/transcriptions")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "transcription.txt")
        
        with open(output_file, "w") as file:
            for item in transcript:
                sentence = item["sentence"]
                start_time, end_time = item["timestamp_start"], item["timestamp_end"]

                file.write(f"{start_time}s to {end_time}s: {sentence}\n")

        return f"Transcription completed successfully. {len(transcript)} sentences transcribed and saved to transcription.txt"

    except FileNotFoundError as f:
        return f"The specified audio file could not be found: {str(f)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def translate_text(input_text, source_language, target_language):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model=os.getenv("model"),
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",
             "content": f"Directly translate the following {source_language} text to a pure {target_language} "
                        f"video subtitle text without additional explanation.: '{input_text}'"},
        ],
        max_tokens=1500
    )

    # Correctly accessing the response content
    translated_text = response.choices[0].message.content if response.choices else None

    return translated_text


def translate_transcript(source_language, target_language):
    transcript_file = get_output_path("output/transcriptions/transcription.txt")
    with open(transcript_file, "r") as f:
        lines = f.readlines()

    translated_transcript = []

    for line in lines:
        # Split each line into timestamp and text parts
        parts = line.strip().split(': ')
        if len(parts) == 2:
            timestamp, text = parts[0], parts[1]

            translated_text = translate_text(text, source_language, target_language)
            translated_line = f"{timestamp}: {translated_text}"
            translated_transcript.append(translated_line)
        else:
            translated_transcript.append(line.strip())

    output_dir = get_output_path("output/transcriptions")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{target_language}_transcription.txt")
    
    with open(output_file, "w") as file:
        for line in translated_transcript:
            file.write(f"{line}\n")

    return f"Translation completed successfully. {len(translated_transcript)} lines translated from {source_language} to {target_language} and saved to {target_language}_transcription.txt"


def generate_recap(target_duration_seconds=30):
    """
    Generate a 30-second recap text and suggest clip timings based on the transcription.
    Uses GPT-4 to analyze the transcript and select the most impactful moments.
    """
    try:
        # Read the transcription
        transcript_file = get_output_path("output/transcriptions/transcription.txt")
        with open(transcript_file, "r") as f:
            transcript_content = f.read()
        
        if not transcript_content.strip():
            return "Error: Transcription file is empty"
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        prompt = f"""Based on the following video transcription with timestamps, create a strictly {target_duration_seconds}-second recap:

{transcript_content}

CRITICAL REQUIREMENTS:
1. A concise recap text that will take EXACTLY {target_duration_seconds} seconds to speak when converted to audio
2. Specific clip timings from the original video that total EXACTLY {target_duration_seconds} seconds (not approximately, but exactly)

Format your response as JSON:
{{
    "recap_text": "Your engaging recap text here (write enough text to fill exactly {target_duration_seconds} seconds of speech)",
    "clip_timings": [
        {{"start": 0, "end": 5, "reason": "Opening statement"}},
        {{"start": 19, "end": 22, "reason": "Key emotional moment"}},
        ...
    ],
    "total_duration": {target_duration_seconds}
}}

IMPORTANT:
- The sum of all clip durations (end - start) MUST equal EXACTLY {target_duration_seconds} seconds
- Calculate: (clip1_end - clip1_start) + (clip2_end - clip2_start) + ... = {target_duration_seconds}
- The recap_text should be long enough to narrate for exactly {target_duration_seconds} seconds (approximately 75-80 words for 30 seconds)
- Capture the most impactful moments
- Ensure clips flow naturally when combined
- Represent the overall tone/message
"""
        
        response = client.chat.completions.create(
            model=os.getenv("model"),
            messages=[
                {"role": "system", "content": "You are a professional video editor skilled at creating engaging recaps. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000
        )
        
        result_text = response.choices[0].message.content if response.choices else None
        
        # Parse JSON from response
        # Remove markdown code blocks if present
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        
        recap_data = json.loads(result_text.strip())
        
        # Save recap data
        output_dir = get_output_path("output/transcriptions")
        os.makedirs(output_dir, exist_ok=True)
        
        recap_data_file = os.path.join(output_dir, "recap_data.json")
        with open(recap_data_file, "w") as f:
            json.dump(recap_data, f, indent=2)
        
        # Save recap text separately
        recap_text_file = os.path.join(output_dir, "recap_text.txt")
        with open(recap_text_file, "w") as f:
            f.write(recap_data.get("recap_text", ""))
        
        clip_count = len(recap_data.get("clip_timings", []))
        total_duration = recap_data.get("total_duration", 0)
        
        return f"Recap generated successfully! Created {clip_count} clip suggestions totaling ~{total_duration} seconds. Data saved to recap_data.json and recap_text.txt"
    
    except FileNotFoundError:
        return "Error: transcription.txt not found. Please run transcription first."
    except json.JSONDecodeError as e:
        return f"Error: Failed to parse AI response as JSON: {str(e)}"
    except Exception as e:
        return f"Error generating recap: {str(e)}"


def extract_video_clips(video_filepath, target_duration=30):
    """
    Extract video clips based on the timings suggested by the recap generator.
    Combines clips into a single recap video of EXACTLY target_duration seconds.
    """
    try:
        # Read the recap data
        recap_data_file = get_output_path("output/transcriptions/recap_data.json")
        with open(recap_data_file, "r") as f:
            recap_data = json.load(f)
        
        clip_timings = recap_data.get("clip_timings", [])
        
        if not clip_timings:
            return "Error: No clip timings found in recap_data.json"
        
        if not os.path.exists(video_filepath):
            return f"Error: Video file not found at {video_filepath}"
        
        # Load the original video
        video = VideoFileClip(video_filepath)
        
        # Extract clips
        clips = []
        total_clips_duration = 0
        for i, timing in enumerate(clip_timings):
            start = timing.get("start", 0)
            end = timing.get("end", start + 1)
            reason = timing.get("reason", "clip")
            
            # Extract subclip
            clip = video.subclip(start, end)
            clips.append(clip)
            total_clips_duration += (end - start)
            
            print(f"Extracted clip {i+1}/{len(clip_timings)}: {start}s-{end}s ({reason})")
        
        # Concatenate clips
        from moviepy.editor import concatenate_videoclips, ColorClip
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # Check duration and adjust to exactly target_duration
        current_duration = final_clip.duration
        print(f"\nCurrent video duration: {current_duration:.2f}s")
        print(f"Target duration: {target_duration}s")
        
        if abs(current_duration - target_duration) > 0.1:  # More than 0.1s difference
            if current_duration < target_duration:
                # Add black frames to reach exactly target_duration
                gap = target_duration - current_duration
                print(f"Adding {gap:.2f}s of black frames to reach {target_duration}s")
                
                # Create black clip with same dimensions
                black_clip = ColorClip(
                    size=final_clip.size,
                    color=(0, 0, 0),
                    duration=gap
                )
                
                # Concatenate with black clip
                final_clip = concatenate_videoclips([final_clip, black_clip], method="compose")
                
            elif current_duration > target_duration:
                # Trim to exactly target_duration
                print(f"Trimming video from {current_duration:.2f}s to {target_duration}s")
                final_clip = final_clip.subclip(0, target_duration)
        
        print(f"✅ Final video duration: {final_clip.duration:.2f}s")
        
        # Save the recap video
        output_dir = get_output_path("output/videos")
        os.makedirs(output_dir, exist_ok=True)
        output_filename = os.path.join(output_dir, "recap_video.mp4")
        
        final_clip.write_videofile(
            output_filename,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True
        )
        
        # Clean up
        video.close()
        final_clip.close()
        for clip in clips:
            clip.close()
        
        return f"Recap video created successfully! {len(clips)} clips combined into {output_filename} (duration: EXACTLY {target_duration} seconds)"
    
    except FileNotFoundError as e:
        return f"Error: Required file not found - {str(e)}"
    except Exception as e:
        return f"Error extracting video clips: {str(e)}"


def remove_audio_from_recap(input_video=None, output_video=None):
    """
    Remove audio from the recap video.
    Useful for adding custom background music or voiceover later.
    
    Args:
        input_video: Path to the input video (default: output/videos/recap_video.mp4)
        output_video: Path for the output video without audio (default: output/videos/recap_video_no_audio.mp4)
    
    Returns:
        Success message string
    """
    try:
        # Use default paths if not provided
        if input_video is None:
            input_video = get_output_path("output/videos/recap_video.mp4")
        if output_video is None:
            output_video = get_output_path("output/videos/recap_video_no_audio.mp4")
        
        if not os.path.exists(input_video):
            return f"Error: Video file not found at {input_video}"
        
        print(f"Removing audio from {input_video}...")
        
        # Load the video
        video = VideoFileClip(input_video)
        
        # Get video without audio
        video_no_audio = video.without_audio()
        
        # Write the output
        video_no_audio.write_videofile(
            output_video,
            codec="libx264",
            audio=False,
            logger=None  # Suppress progress bars
        )
        
        # Clean up
        video.close()
        video_no_audio.close()
        
        # Get file sizes
        input_size = os.path.getsize(input_video) / (1024 * 1024)  # MB
        output_size = os.path.getsize(output_video) / (1024 * 1024)  # MB
        
        return f"Audio removed successfully! Output saved to {output_video} (Reduced from {input_size:.2f}MB to {output_size:.2f}MB)"
    
    except Exception as e:
        return f"Error removing audio: {str(e)}"