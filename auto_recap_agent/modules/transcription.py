"""
Modular Video Transcription and Recap Generation

This module contains individual functions for each step of the workflow.
Each function is independent and can be called separately.
"""

import os
import json
import whisper
from moviepy.editor import VideoFileClip

# Get the directory where this file is located (parent of modules/)
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
    
    # Load Whisper model
    model = whisper.load_model(model_size)
    
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
    
    return txt_file


def translate_transcription(input_file, source_lang, target_lang, output_dir="output/transcriptions"):
    """
    Step 2: Translate transcription to another language
    
    Args:
        input_file: Path to transcription.txt file
        source_lang: Source language (e.g., "English")
        target_lang: Target language (e.g., "Tamil")
        output_dir: Directory to save translation
    
    Returns:
        Path to translated file
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
    
    # Read transcription
    with open(input_file, "r") as f:
        lines = f.readlines()
    
    # Translate each line
    translated_lines = []
    for i, line in enumerate(lines, 1):
        parts = line.strip().split(': ', 1)
        if len(parts) == 2:
            timestamp, text = parts
            
            print(f"Translating line {i}/{len(lines)}...", end='\r')
            
            response = client.chat.completions.create(
                model=os.getenv("model", "gpt-4"),
                messages=[
                    {"role": "system", "content": "You are a professional translator."},
                    {"role": "user", "content": f"Translate this {source_lang} text to {target_lang}: {text}"}
                ],
                max_tokens=500
            )
            
            translated_text = response.choices[0].message.content if response.choices else text
            translated_lines.append(f"{timestamp}: {translated_text}")
        else:
            translated_lines.append(line.strip())
    
    print()  # New line after progress
    
    # Save translation
    output_path = get_output_path(output_dir)
    os.makedirs(output_path, exist_ok=True)
    
    output_file = os.path.join(output_path, f"{target_lang.lower()}_transcription.txt")
    with open(output_file, "w") as f:
        for line in translated_lines:
            f.write(f"{line}\n")
    
    print(f"✅ Translation complete!")
    print(f"   Lines translated: {len(translated_lines)}")
    print(f"   Output: {output_file}")
    
    return output_file


# Export functions
__all__ = [
    'transcribe_video',
    'translate_transcription',
    'get_output_path'
]

