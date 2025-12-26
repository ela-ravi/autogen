#!/usr/bin/env python3
"""
Resume Workflow: From TTS Generation

Use this when you already have recap video clips and want to:
- Skip: Audio extraction, Transcription, AI Recap, Video Clips
- Start: TTS Generation → Final Video

Prerequisites:
    - output/videos/recap_video.mp4 must exist
    - output/transcriptions/recap_text.txt must exist

Usage:
    python resume/from_tts_generation.py [options]
    
Example:
    python resume/from_tts_generation.py --voice shimmer
    python resume/from_tts_generation.py --tts-model tts-1-hd --voice alloy
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.audio_processing import generate_tts_audio, merge_audio_with_video


def print_header(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(description="Resume workflow from TTS generation")
    parser.add_argument("--tts-model", default="tts-1", help="TTS model to use")
    parser.add_argument("--voice", default="nova", help="TTS voice to use")
    parser.add_argument("--recap-video", default="output/videos/recap_video.mp4",
                       help="Path to existing recap video")
    parser.add_argument("--recap-text", default="output/transcriptions/recap_text.txt",
                       help="Path to existing recap text file")
    
    args = parser.parse_args()
    
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*20 + "RESUME FROM TTS GENERATION" + " "*32 + "║")
    print("╚" + "="*78 + "╝")
    
    # Check if files exist
    if not os.path.exists(args.recap_video):
        print(f"\n❌ Error: Recap video not found: {args.recap_video}")
        print("   Run clip extraction first or provide correct path with --recap-video")
        sys.exit(1)
    
    if not os.path.exists(args.recap_text):
        print(f"\n❌ Error: Recap text not found: {args.recap_text}")
        print("   Run recap generation first or provide correct path with --recap-text")
        sys.exit(1)
    
    print(f"\n✅ Using existing recap video: {args.recap_video}")
    print(f"✅ Using existing recap text: {args.recap_text}")
    
    try:
        # Step 1: Generate TTS
        print_header("STEP 1/2: Generate TTS Audio")
        tts_audio = generate_tts_audio(
            recap_text_file=args.recap_text,
            tts_model=args.tts_model,
            tts_voice=args.voice
        )
        
        # Step 2: Merge audio+video
        print_header("STEP 2/2: Merge Audio with Video")
        final_video = merge_audio_with_video(
            video_path=args.recap_video,
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

