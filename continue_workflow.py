#!/usr/bin/env python3
"""
Continue Workflow - Resume from where it failed

This script continues the workflow from the video clip extraction step,
avoiding re-running transcription and recap generation to save API costs.
"""

import os
import sys

# Add transcribe_video to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'transcribe_video'))

from functions import extract_video_clips
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'transcribe_video', 'scripts'))
from generate_tts_audio import generate_timed_recap_audio, merge_audio_with_video

def continue_workflow(video_filepath):
    """Continue the workflow from clip extraction."""
    
    print("=" * 70)
    print("CONTINUING WORKFLOW FROM CLIP EXTRACTION")
    print("=" * 70)
    
    # Step 1: Extract video clips
    print("\n[Step 1/3] Extracting video clips...")
    print(f"Video: {video_filepath}")
    result = extract_video_clips(video_filepath, target_duration=30)
    print(f"✅ {result}\n")
    
    if "Error" in result:
        print("❌ Failed at clip extraction. Cannot continue.")
        return
    
    # Step 2: Generate TTS audio
    print("\n[Step 2/3] Generating TTS audio narration...")
    result = generate_timed_recap_audio(target_duration=30)
    print(f"✅ {result}\n")
    
    if "Error" in result:
        print("❌ Failed at TTS generation. Cannot continue.")
        return
    
    # Step 3: Merge audio with video
    print("\n[Step 3/3] Merging audio with video...")
    result = merge_audio_with_video()
    print(f"✅ {result}\n")
    
    if "Error" in result:
        print("❌ Failed at audio merge.")
        return
    
    print("=" * 70)
    print("✅ WORKFLOW COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\n📹 Final output:")
    print("   transcribe_video/output/videos/recap_video_with_narration.mp4")
    print()

if __name__ == "__main__":
    # Use the same video file from the terminal
    video_path = "/Users/ravi/Downloads/NOW_OR_NEVER_5_min.mp4"
    
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        print(f"❌ Error: Video file not found: {video_path}")
        print("\nUsage:")
        print(f"  python continue_workflow.py <video_path>")
        sys.exit(1)
    
    try:
        continue_workflow(video_path)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

