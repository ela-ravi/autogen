#!/usr/bin/env python3
"""
Resume Workflow: From Audio Merge

Use this when you already have recap video and TTS audio and want to:
- Skip: Everything except final merge
- Start: Merge Audio with Video

Prerequisites:
    - output/videos/recap_video.mp4 must exist
    - output/audio/recap_narration.mp3 must exist

Usage:
    python resume/from_audio_merge.py [options]
    
Example:
    python resume/from_audio_merge.py
    python resume/from_audio_merge.py --recap-video output/videos/recap_video.mp4
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.audio_processing import merge_audio_with_video


def print_header(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(description="Resume workflow from audio merge")
    parser.add_argument("--recap-video", default="output/videos/recap_video.mp4",
                       help="Path to existing recap video")
    parser.add_argument("--tts-audio", default="output/audio/recap_narration.mp3",
                       help="Path to existing TTS audio file")
    
    args = parser.parse_args()
    
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*22 + "RESUME FROM AUDIO MERGE" + " "*33 + "║")
    print("╚" + "="*78 + "╝")
    
    # Check if files exist
    if not os.path.exists(args.recap_video):
        print(f"\n❌ Error: Recap video not found: {args.recap_video}")
        print("   Run clip extraction first or provide correct path with --recap-video")
        sys.exit(1)
    
    if not os.path.exists(args.tts_audio):
        print(f"\n❌ Error: TTS audio not found: {args.tts_audio}")
        print("   Run TTS generation first or provide correct path with --tts-audio")
        sys.exit(1)
    
    print(f"\n✅ Using existing recap video: {args.recap_video}")
    print(f"✅ Using existing TTS audio: {args.tts_audio}")
    
    try:
        # Step 1: Merge audio+video
        print_header("STEP 1/1: Merge Audio with Video")
        final_video = merge_audio_with_video(
            video_path=args.recap_video,
            audio_path=args.tts_audio
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

