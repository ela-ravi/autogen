#!/usr/bin/env python3
"""
Complete Workflow - End-to-End Video Recap Generation

This script orchestrates the entire workflow:
1. Runs transcribe.py (transcription + translation + recap generation + video extraction)
2. Generates TTS audio narration
3. Merges audio with video to create final output

Usage:
    python run_complete_workflow.py
"""

import os
import sys
import subprocess

# Add transcribe_video to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'transcribe_video'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'transcribe_video', 'scripts'))

from generate_tts_audio import generate_timed_recap_audio, merge_audio_with_video


def run_transcription_workflow():
    """Run the main transcribe.py script."""
    print("\n" + "=" * 80)
    print("STEP 1: RUNNING TRANSCRIPTION & RECAP GENERATION WORKFLOW")
    print("=" * 80)
    
    # Run transcribe.py
    transcribe_script = os.path.join(os.path.dirname(__file__), 'transcribe_video', 'transcribe.py')
    result = subprocess.run([sys.executable, transcribe_script], cwd=os.path.dirname(__file__))
    
    if result.returncode != 0:
        print("\n❌ Transcription workflow failed!")
        return False
    
    print("\n✅ Transcription workflow completed!")
    return True


def generate_audio():
    """Generate TTS audio narration."""
    print("\n" + "=" * 80)
    print("STEP 2: GENERATING TTS AUDIO NARRATION")
    print("=" * 80)
    
    try:
        result = generate_timed_recap_audio(target_duration=30)
        print(f"\n✅ {result}")
        
        if "Error" in result:
            print("\n❌ TTS audio generation failed!")
            return False
        
        return True
    except Exception as e:
        print(f"\n❌ Error generating audio: {e}")
        import traceback
        traceback.print_exc()
        return False


def merge_audio_video():
    """Merge audio with video."""
    print("\n" + "=" * 80)
    print("STEP 3: MERGING AUDIO WITH VIDEO")
    print("=" * 80)
    
    try:
        result = merge_audio_with_video()
        print(f"\n✅ {result}")
        
        if "Error" in result:
            print("\n❌ Audio-video merge failed!")
            return False
        
        return True
    except Exception as e:
        print(f"\n❌ Error merging audio with video: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_final_summary():
    """Show final summary of generated files."""
    print("\n" + "=" * 80)
    print("🎉 COMPLETE WORKFLOW FINISHED SUCCESSFULLY!")
    print("=" * 80)
    
    output_dir = os.path.join(os.path.dirname(__file__), 'transcribe_video', 'output')
    
    print("\n📁 Generated Files:")
    print("-" * 80)
    
    files_to_check = [
        ("transcriptions/transcription.txt", "Original transcription"),
        ("transcriptions/recap_data.json", "Recap metadata (AI suggestions)"),
        ("transcriptions/recap_text.txt", "Recap narration text"),
        ("videos/recap_video.mp4", "Recap video (no narration)"),
        ("audio/recap_narration_timed.mp3", "TTS audio narration"),
        ("videos/recap_video_with_narration.mp4", "⭐ FINAL OUTPUT - Recap with narration"),
    ]
    
    for rel_path, description in files_to_check:
        full_path = os.path.join(output_dir, rel_path)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            size_str = f"{size / (1024*1024):.2f} MB" if size > 1024*1024 else f"{size / 1024:.2f} KB"
            print(f"✅ {rel_path}")
            print(f"   {description} ({size_str})")
        else:
            print(f"⚠️  {rel_path} - Not found")
    
    print("\n" + "=" * 80)
    print("📺 Your final recap video is ready at:")
    print(f"   transcribe_video/output/videos/recap_video_with_narration.mp4")
    print("=" * 80 + "\n")


def main():
    """Main function to run the complete workflow."""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                  COMPLETE VIDEO RECAP GENERATION WORKFLOW                  ║
║                                                                            ║
║  This script will:                                                         ║
║  1. Transcribe your video                                                  ║
║  2. Translate the transcript (optional)                                    ║
║  3. Generate AI-powered recap suggestions                                  ║
║  4. Extract and combine video clips                                        ║
║  5. Generate TTS audio narration                                           ║
║  6. Merge audio with video for final output                                ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Step 1: Run transcribe.py workflow
        if not run_transcription_workflow():
            sys.exit(1)
        
        # Check if recap video was created
        recap_video = os.path.join(
            os.path.dirname(__file__), 
            'transcribe_video', 
            'output', 
            'videos', 
            'recap_video.mp4'
        )
        
        if not os.path.exists(recap_video):
            print("\n⚠️  Recap video was not created. Skipping audio generation.")
            print("   (User may have chosen not to create a recap)")
            sys.exit(0)
        
        # Step 2: Generate TTS audio
        if not generate_audio():
            sys.exit(1)
        
        # Step 3: Merge audio with video
        if not merge_audio_video():
            sys.exit(1)
        
        # Show final summary
        show_final_summary()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

