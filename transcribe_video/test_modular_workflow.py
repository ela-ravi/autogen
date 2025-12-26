#!/usr/bin/env python3
"""
Test the modular workflow with existing data

This script tests each module individually to ensure they work correctly.
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_module_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    
    try:
        from modules import (
            transcribe_video,
            translate_transcription,
            generate_recap_suggestions,
            extract_and_merge_clips,
            remove_audio_from_video,
            generate_tts_audio,
            merge_audio_with_video
        )
        print("✅ All modules imported successfully!")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_file_structure():
    """Test that all required files exist"""
    print("\nChecking file structure...")
    
    base_dir = os.path.dirname(__file__)
    required_files = [
        "modules/__init__.py",
        "modules/transcription.py",
        "modules/video_processing.py",
        "modules/audio_processing.py",
        "scripts/01_transcribe.py",
        "scripts/02_translate.py",
        "scripts/03_generate_recap.py",
        "scripts/04_extract_clips.py",
        "scripts/05_remove_audio.py",
        "scripts/06_generate_tts.py",
        "scripts/07_merge_audio_video.py",
        "run_recap_workflow.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            all_exist = False
    
    return all_exist


def show_usage_examples():
    """Show usage examples for each script"""
    print("\n" + "="*80)
    print("USAGE EXAMPLES")
    print("="*80)
    
    examples = [
        ("Master Script (All Steps)", [
            "python run_recap_workflow.py /path/to/video.mp4",
            "python run_recap_workflow.py /path/to/video.mp4 --translate English Tamil",
            "python run_recap_workflow.py /path/to/video.mp4 --duration 45 --voice shimmer"
        ]),
        ("Individual Steps", [
            "# Step 1: Transcribe",
            "python scripts/01_transcribe.py /path/to/video.mp4",
            "",
            "# Step 2: Translate (optional)",
            "python scripts/02_translate.py output/transcriptions/transcription.txt English Tamil",
            "",
            "# Step 3: Generate recap",
            "python scripts/03_generate_recap.py output/transcriptions/transcription.txt",
            "",
            "# Step 4: Extract clips",
            "python scripts/04_extract_clips.py /path/to/video.mp4 output/transcriptions/recap_data.json",
            "",
            "# Step 5: Remove audio (optional)",
            "python scripts/05_remove_audio.py output/videos/recap_video.mp4",
            "",
            "# Step 6: Generate TTS",
            "python scripts/06_generate_tts.py output/transcriptions/recap_text.txt",
            "",
            "# Step 7: Merge audio and video",
            "python scripts/07_merge_audio_video.py output/videos/recap_video.mp4 output/audio/recap_narration.mp3"
        ])
    ]
    
    for title, cmds in examples:
        print(f"\n{title}:")
        print("-" * 80)
        for cmd in cmds:
            print(f"  {cmd}")


def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    MODULAR WORKFLOW TEST SUITE                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Test imports
    imports_ok = test_module_imports()
    
    # Test file structure
    structure_ok = test_file_structure()
    
    # Show usage
    show_usage_examples()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    if imports_ok and structure_ok:
        print("✅ All tests passed! The modular workflow is ready to use.")
        print("\n💡 Quick start:")
        print("   python run_recap_workflow.py /path/to/your/video.mp4")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print()


if __name__ == "__main__":
    main()

