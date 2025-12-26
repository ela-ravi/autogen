#!/usr/bin/env python3
"""
Update File Paths Script

This script updates all file paths in functions.py and generate_tts_audio.py
to use the new output directory structure.
"""

import os
import re

def update_functions_py():
    """Update file paths in functions.py"""
    
    print("Updating functions.py...")
    
    file_path = "transcribe_video/functions.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Update transcription output paths
    content = content.replace(
        'with open("transcription.txt", "w")',
        'with open("output/transcriptions/transcription.txt", "w")'
    )
    
    content = content.replace(
        'with open("transcription.txt", "r")',
        'with open("output/transcriptions/transcription.txt", "r")'
    )
    
    # Update translation output paths
    content = content.replace(
        'with open(f"{target_language}_transcription.txt", "w")',
        'with open(f"output/transcriptions/{target_language}_transcription.txt", "w")'
    )
    
    # Update recap data paths
    content = content.replace(
        'with open("recap_data.json", "w")',
        'with open("output/transcriptions/recap_data.json", "w")'
    )
    
    content = content.replace(
        'with open("recap_text.txt", "w")',
        'with open("output/transcriptions/recap_text.txt", "w")'
    )
    
    content = content.replace(
        'with open("recap_data.json", "r")',
        'with open("output/transcriptions/recap_data.json", "r")'
    )
    
    # Update video output paths
    content = content.replace(
        'output_filename = "recap_video.mp4"',
        'output_filename = "output/videos/recap_video.mp4"'
    )
    
    # Update audio removal paths
    content = re.sub(
        r'def remove_audio_from_recap\(input_video="recap_video\.mp4", output_video="recap_video_no_audio\.mp4"\)',
        'def remove_audio_from_recap(input_video="output/videos/recap_video.mp4", output_video="output/videos/recap_video_no_audio.mp4")',
        content
    )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ functions.py updated")


def update_generate_tts_audio_py():
    """Update file paths in generate_tts_audio.py"""
    
    print("\nUpdating generate_tts_audio.py...")
    
    file_path = "transcribe_video/scripts/generate_tts_audio.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Update recap_text.txt path
    content = content.replace(
        'if os.path.exists("recap_text.txt"):',
        'if os.path.exists("output/transcriptions/recap_text.txt"):'
    )
    
    content = content.replace(
        'with open("recap_text.txt", "r")',
        'with open("output/transcriptions/recap_text.txt", "r")'
    )
    
    # Update output audio path
    content = content.replace(
        'output_audio_path="recap_narration.mp3"',
        'output_audio_path="output/audio/recap_narration.mp3"'
    )
    
    content = content.replace(
        'output_audio_path="recap_narration_timed.mp3"',
        'output_audio_path="output/audio/recap_narration_timed.mp3"'
    )
    
    # Update recap_data.json path
    content = content.replace(
        'if not os.path.exists("recap_data.json"):',
        'if not os.path.exists("output/transcriptions/recap_data.json"):'
    )
    
    content = content.replace(
        'with open("recap_data.json", "r")',
        'with open("output/transcriptions/recap_data.json", "r")'
    )
    
    # Update video merge paths
    content = re.sub(
        r'def merge_audio_with_video\(\s*video_path="recap_video\.mp4",\s*audio_path="recap_narration_timed\.mp3",\s*output_path="recap_video_with_narration\.mp4"',
        'def merge_audio_with_video(\n    video_path="output/videos/recap_video.mp4",\n    audio_path="output/audio/recap_narration_timed.mp3",\n    output_path="output/videos/recap_video_with_narration.mp4"',
        content
    )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ generate_tts_audio.py updated")


def create_output_directories():
    """Ensure output directories exist"""
    
    print("\nCreating output directories...")
    
    directories = [
        "transcribe_video/output",
        "transcribe_video/output/transcriptions",
        "transcribe_video/output/videos",
        "transcribe_video/output/audio"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ {directory}/")


def main():
    print("="*70)
    print("UPDATING FILE PATHS FOR NEW STRUCTURE")
    print("="*70)
    print()
    
    try:
        create_output_directories()
        update_functions_py()
        update_generate_tts_audio_py()
        
        print()
        print("="*70)
        print("✅ ALL FILE PATHS UPDATED!")
        print("="*70)
        print()
        print("Updated files:")
        print("  • transcribe_video/functions.py")
        print("  • transcribe_video/scripts/generate_tts_audio.py")
        print()
        print("All scripts will now use the output/ directory structure!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

