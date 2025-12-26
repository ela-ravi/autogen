#!/usr/bin/env python3
"""
Demo script showing how to use the recap generation features independently.
This can be useful for testing or integrating into other workflows.
"""

import os
import json
from functions import (
    recognize_transcript_from_video,
    translate_transcript,
    generate_recap,
    extract_video_clips
)

def demo_recap_generation(video_path, create_clips=True):
    """
    Demonstrates the complete recap generation workflow.
    
    Args:
        video_path: Path to the video file
        create_clips: Whether to actually extract and create clips (default: True)
    """
    print("=" * 60)
    print("AI VIDEO RECAP GENERATOR - DEMO")
    print("=" * 60)
    
    # Step 1: Transcribe
    print("\n[Step 1/4] Transcribing video...")
    print(f"Video: {video_path}")
    result = recognize_transcript_from_video(video_path)
    print(f"✓ {result}")
    
    # Step 2: Show transcription
    print("\n[Step 2/4] Reading transcription...")
    if os.path.exists("transcription.txt"):
        with open("transcription.txt", "r") as f:
            lines = f.readlines()
        print(f"✓ Found {len(lines)} timestamped segments")
        print("\nFirst 3 segments:")
        for line in lines[:3]:
            print(f"  {line.strip()}")
        if len(lines) > 3:
            print(f"  ... and {len(lines) - 3} more")
    
    # Step 3: Generate recap
    print("\n[Step 3/4] Generating AI-powered recap...")
    result = generate_recap(target_duration_seconds=30)
    print(f"✓ {result}")
    
    # Show recap data
    if os.path.exists("recap_data.json"):
        with open("recap_data.json", "r") as f:
            recap_data = json.load(f)
        
        print("\n📝 Recap Text:")
        print(f"  {recap_data.get('recap_text', 'N/A')}")
        
        print(f"\n🎬 Suggested Clips ({len(recap_data.get('clip_timings', []))} clips):")
        for i, clip in enumerate(recap_data.get('clip_timings', []), 1):
            duration = clip['end'] - clip['start']
            print(f"  {i}. {clip['start']}s - {clip['end']}s ({duration}s) - {clip.get('reason', 'N/A')}")
        
        print(f"\n⏱️  Total Duration: ~{recap_data.get('total_duration', 0)} seconds")
    
    # Step 4: Extract clips (optional)
    if create_clips:
        print("\n[Step 4/4] Extracting and combining video clips...")
        print("⚠️  This may take a minute...")
        result = extract_video_clips(video_path)
        print(f"✓ {result}")
        
        if os.path.exists("recap_video.mp4"):
            file_size = os.path.getsize("recap_video.mp4") / (1024 * 1024)  # MB
            print(f"\n🎉 Recap video created: recap_video.mp4 ({file_size:.2f} MB)")
    else:
        print("\n[Step 4/4] Skipping clip extraction (create_clips=False)")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED")
    print("=" * 60)


def demo_translation(source_lang="English", target_lang="Spanish"):
    """
    Demonstrates translation functionality.
    """
    print("\n" + "=" * 60)
    print("TRANSLATION DEMO")
    print("=" * 60)
    
    if not os.path.exists("transcription.txt"):
        print("❌ Error: transcription.txt not found")
        print("   Please run transcription first")
        return
    
    print(f"\nTranslating from {source_lang} to {target_lang}...")
    result = translate_transcript(source_lang, target_lang)
    print(f"✓ {result}")
    
    output_file = f"{target_lang}_transcription.txt"
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            lines = f.readlines()
        print(f"\nFirst 3 translated lines:")
        for line in lines[:3]:
            print(f"  {line.strip()}")


def quick_test():
    """
    Quick test to verify all functions are working.
    """
    print("\n" + "=" * 60)
    print("QUICK FUNCTION TEST")
    print("=" * 60)
    
    tests = [
        ("recognize_transcript_from_video", recognize_transcript_from_video),
        ("translate_transcript", translate_transcript),
        ("generate_recap", generate_recap),
        ("extract_video_clips", extract_video_clips),
    ]
    
    print("\nChecking function imports...")
    for name, func in tests:
        try:
            assert callable(func)
            print(f"✓ {name} - OK")
        except Exception as e:
            print(f"❌ {name} - FAILED: {e}")
    
    print("\nChecking required files...")
    files = {
        "transcription.txt": "Transcription data",
        "recap_data.json": "Recap metadata",
        "recap_text.txt": "Recap narration",
        "recap_video.mp4": "Final recap video"
    }
    
    for filename, description in files.items():
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✓ {filename} - Found ({size} bytes) - {description}")
        else:
            print(f"⚠️  {filename} - Not found - {description}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    import sys
    
    print("""
╔══════════════════════════════════════════════════════════╗
║        AI VIDEO RECAP GENERATOR - DEMO SCRIPT           ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Show usage
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python demo.py <video_path>          - Full demo with clip extraction")
        print("  python demo.py <video_path> --no-clips - Demo without clip extraction")
        print("  python demo.py --test                - Quick function test")
        print("\nExamples:")
        print("  python demo.py /path/to/video.mp4")
        print("  python demo.py /path/to/video.mp4 --no-clips")
        print("  python demo.py --test")
        sys.exit(1)
    
    # Handle test mode
    if sys.argv[1] == "--test":
        quick_test()
        sys.exit(0)
    
    # Get video path
    video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        print(f"❌ Error: Video file not found: {video_path}")
        sys.exit(1)
    
    # Check if --no-clips flag is present
    create_clips = "--no-clips" not in sys.argv
    
    try:
        # Run demo
        demo_recap_generation(video_path, create_clips=create_clips)
        
        # Optional: Show translation demo
        show_translation = input("\n\nDo you want to see translation demo? (yes/no): ").strip().lower()
        if show_translation in ['yes', 'y']:
            target_lang = input("Target language (e.g., Spanish, French, Tamil): ").strip()
            demo_translation("English", target_lang)
        
        print("\n✅ All done!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

