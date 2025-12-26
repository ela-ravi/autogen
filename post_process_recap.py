#!/usr/bin/env python3
"""
Post-Processing Script - TTS Audio Generation and Merging

This script handles the post-processing steps after transcribe.py has completed:
1. Generates TTS audio narration from recap text
2. Merges the audio with the recap video

Use this when you've already run transcribe.py and just need the audio steps.

Usage:
    python post_process_recap.py
"""

import os
import sys

# Add transcribe_video to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'transcribe_video'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'transcribe_video', 'scripts'))

from generate_tts_audio import generate_timed_recap_audio, merge_audio_with_video


def check_prerequisites():
    """Check if required files exist."""
    print("Checking prerequisites...")
    
    base_dir = os.path.join(os.path.dirname(__file__), 'transcribe_video', 'output')
    
    required_files = {
        'recap_video': os.path.join(base_dir, 'videos', 'recap_video.mp4'),
        'recap_text': os.path.join(base_dir, 'transcriptions', 'recap_text.txt'),
        'recap_data': os.path.join(base_dir, 'transcriptions', 'recap_data.json'),
    }
    
    missing = []
    for name, path in required_files.items():
        if not os.path.exists(path):
            missing.append((name, path))
        else:
            print(f"✅ Found {name}")
    
    if missing:
        print("\n❌ Missing required files:")
        for name, path in missing:
            print(f"   - {name}: {path}")
        print("\n💡 Please run transcribe.py first to generate the recap video and text.")
        return False
    
    print("✅ All prerequisites met!\n")
    return True


def main():
    """Main function for post-processing."""
    print("""
╔══════════════════════════════════════════════════════════╗
║        RECAP VIDEO POST-PROCESSING                       ║
║                                                          ║
║  This script will:                                       ║
║  1. Generate TTS audio narration from recap text         ║
║  2. Merge audio with recap video                         ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    try:
        # Step 1: Generate TTS audio
        print("=" * 70)
        print("STEP 1: GENERATING TTS AUDIO NARRATION")
        print("=" * 70 + "\n")
        
        result = generate_timed_recap_audio(target_duration=30)
        print(f"\n{result}\n")
        
        if "Error" in result:
            print("❌ Failed to generate audio!")
            sys.exit(1)
        
        print("✅ Audio generation complete!\n")
        
        # Step 2: Merge audio with video
        print("=" * 70)
        print("STEP 2: MERGING AUDIO WITH VIDEO")
        print("=" * 70 + "\n")
        
        result = merge_audio_with_video()
        print(f"\n{result}\n")
        
        if "Error" in result:
            print("❌ Failed to merge audio with video!")
            sys.exit(1)
        
        # Success!
        print("\n" + "=" * 70)
        print("🎉 POST-PROCESSING COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        
        final_video = os.path.join(
            os.path.dirname(__file__), 
            'transcribe_video', 
            'output', 
            'videos', 
            'recap_video_with_narration.mp4'
        )
        
        if os.path.exists(final_video):
            size = os.path.getsize(final_video) / (1024 * 1024)
            print(f"\n📹 Final video: {final_video}")
            print(f"   Size: {size:.2f} MB")
            print(f"   Duration: 30 seconds")
        
        print("\n" + "=" * 70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

