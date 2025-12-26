#!/usr/bin/env python3
"""
Quick test script to verify the audio merge fix
"""

import os
import sys

print("Testing audio merge fix...\n")

# Check if required files exist
required_files = [
    "recap_video.mp4",
    "recap_narration_timed.mp3"
]

missing_files = [f for f in required_files if not os.path.exists(f)]

if missing_files:
    print(f"❌ Missing files: {', '.join(missing_files)}")
    print("\nPlease run:")
    print("1. python transcribe.py  (to generate recap_video.mp4)")
    print("2. python generate_tts_audio.py  (to generate audio)")
    sys.exit(1)

print("✅ Required files found")
print("\nAttempting to merge audio with video...")

from generate_tts_audio import merge_audio_with_video

try:
    result = merge_audio_with_video()
    print(f"\n{result}")
    
    if "Error" not in result:
        print("\n✅ SUCCESS! The audio merge error is fixed!")
    else:
        print(f"\n❌ Still has errors")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

