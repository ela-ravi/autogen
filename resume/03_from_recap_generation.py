#!/usr/bin/env python3
"""
Resume Workflow: From Recap Generation

Use this when you already have transcription and want to:
- Skip: Audio extraction, Transcription
- Start: AI Recap → Clips → TTS → Final Video

Prerequisites:
    - output/transcriptions/transcription.txt must exist

Usage:
    python resume/from_recap_generation.py /path/to/video.mp4 [options]
    
Example:
    python resume/from_recap_generation.py /path/to/video.mp4 --duration 45
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.video_processing import generate_recap_suggestions, extract_and_merge_clips, remove_audio_from_video
from modules.audio_processing import generate_tts_audio, merge_audio_with_video


def print_header(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(description="Resume workflow from recap generation")
    parser.add_argument("video_path", help="Path to the original video file")
    parser.add_argument("--duration", type=int, default=30, help="Target recap duration in seconds")
    parser.add_argument("--tts-model", default="tts-1", help="TTS model to use")
    parser.add_argument("--voice", default="nova", help="TTS voice to use")
    parser.add_argument("--remove-original-audio", action="store_true", 
                       help="Remove original audio before adding narration")
    parser.add_argument("--transcription", default="output/transcriptions/transcription.txt",
                       help="Path to existing transcription file")
    
    args = parser.parse_args()
    
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*18 + "RESUME FROM RECAP GENERATION" + " "*32 + "║")
    print("╚" + "="*78 + "╝")
    
    # Check if transcription exists
    if not os.path.exists(args.transcription):
        print(f"\n❌ Error: Transcription file not found: {args.transcription}")
        print("   Run transcription first or provide correct path with --transcription")
        sys.exit(1)
    
    print(f"\n✅ Using existing transcription: {args.transcription}")
    
    try:
        # Step 1: Generate AI recap
        print_header("STEP 1/5: Generate AI Recap Suggestions")
        recap_data_file = generate_recap_suggestions(
            transcription_file=args.transcription,
            target_duration=args.duration
        )
        
        # Step 2: Extract clips
        print_header("STEP 2/5: Extract and Merge Video Clips")
        recap_video = extract_and_merge_clips(
            video_path=args.video_path,
            recap_data_file=recap_data_file,
            target_duration=args.duration
        )
        
        # Step 3: Remove original audio (optional)
        if args.remove_original_audio:
            print_header("STEP 3/5: Remove Original Audio")
            recap_video = remove_audio_from_video(recap_video)
        else:
            print_header("STEP 3/5: Remove Original Audio (Skipped)")
        
        # Step 4: Generate TTS
        print_header("STEP 4/5: Generate TTS and Merge")
        recap_text_file = recap_data_file.replace("recap_data.json", "recap_text.txt")
        tts_audio = generate_tts_audio(
            recap_text_file=recap_text_file,
            tts_model=args.tts_model,
            tts_voice=args.voice
        )
        
        # Step 5: Merge audio+video
        final_video = merge_audio_with_video(
            video_path=recap_video,
            audio_path=tts_audio
        )
        
        print("\n" + "="*80)
        print("✅ WORKFLOW COMPLETE!")
        print("="*80)
        print(f"\n📹 Final video: {final_video}")
        print(f"📁 All files: video_recap_agent/output/\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

