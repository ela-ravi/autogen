#!/usr/bin/env python3
"""
Resume Workflow: Interactive Menu

Interactive script to resume workflow from any checkpoint.
Automatically detects which files exist and suggests appropriate starting points.

Usage:
    python resume_workflow.py /path/to/video.mp4
    python resume_workflow.py  # For steps that don't need video path
"""

import sys
import os
import argparse

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_file_exists(filepath):
    """Check if a file exists"""
    return os.path.exists(filepath)


def print_checkpoint_status():
    """Print status of all checkpoints"""
    checkpoints = [
        ("Audio Extraction", "output/original/extracted_audio.wav"),
        ("Transcription", "output/transcriptions/transcription.txt"),
        ("AI Recap Generation", "output/transcriptions/recap_data.json"),
        ("Video Clip Extraction", "output/videos/recap_video.mp4"),
        ("TTS Generation", "output/audio/recap_narration.mp3"),
        ("Final Video", "output/videos/recap_video_with_narration.mp4"),
    ]
    
    print("\n" + "="*80)
    print("CHECKPOINT STATUS")
    print("="*80)
    
    for name, filepath in checkpoints:
        exists = check_file_exists(filepath)
        status = "✅" if exists else "❌"
        print(f"{status} {name:25} {filepath}")
    
    print("="*80 + "\n")


def get_suggested_starting_point():
    """Determine the best starting point based on existing files"""
    if not check_file_exists("output/original/extracted_audio.wav"):
        return 1, "Start from beginning (no files found)"
    elif not check_file_exists("output/transcriptions/transcription.txt"):
        return 2, "Resume from Transcription (audio exists)"
    elif not check_file_exists("output/transcriptions/recap_data.json"):
        return 3, "Resume from AI Recap (transcription exists)"
    elif not check_file_exists("output/videos/recap_video.mp4"):
        return 4, "Resume from Clip Extraction (recap exists)"
    elif not check_file_exists("output/audio/recap_narration.mp3"):
        return 5, "Resume from TTS Generation (video exists)"
    elif not check_file_exists("output/videos/recap_video_with_narration.mp4"):
        return 6, "Resume from Audio Merge (all components exist)"
    else:
        return 7, "All files exist - regenerate specific step"


def show_menu():
    """Show interactive menu"""
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*25 + "RESUME WORKFLOW MENU" + " "*34 + "║")
    print("╚" + "="*78 + "╝\n")
    
    print("Choose where to resume the workflow:\n")
    print("  1. From Audio Extraction     (Full workflow - start from scratch)")
    print("  2. From Transcription        (Skip: Audio extraction)")
    print("  3. From AI Recap Generation  (Skip: Audio + Transcription)")
    print("  4. From Clip Extraction      (Skip: Audio + Transcription + Recap)")
    print("  5. From TTS Generation       (Skip: Audio + Transcription + Recap + Clips)")
    print("  6. From Audio Merge          (Skip: Everything except final merge)")
    print("  0. Exit\n")
    
    suggested_step, reason = get_suggested_starting_point()
    print(f"💡 Suggestion: Option {suggested_step} - {reason}\n")
    
    while True:
        try:
            choice = input("Enter your choice (0-6): ").strip()
            if choice == "":
                print(f"   Using suggested option: {suggested_step}")
                return suggested_step
            choice_int = int(choice)
            if 0 <= choice_int <= 6:
                return choice_int
            else:
                print("   Invalid choice. Please enter 0-6.")
        except ValueError:
            print("   Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            sys.exit(0)


def run_workflow(choice, video_path=None, extra_args=None):
    """Run the selected workflow"""
    extra_args = extra_args or []
    
    workflows = {
        1: ("resume/01_from_audio_extraction.py", True),
        2: ("resume/02_from_transcription.py", True),
        3: ("resume/03_from_recap_generation.py", True),
        4: ("resume/04_from_clip_extraction.py", True),
        5: ("resume/05_from_tts_generation.py", False),
        6: ("resume/06_from_audio_merge.py", False),
    }
    
    if choice not in workflows:
        print("Invalid choice")
        return
    
    script, needs_video = workflows[choice]
    
    if needs_video and not video_path:
        print("\n❌ Error: Video path required for this step")
        print(f"   Usage: python resume_workflow.py /path/to/video.mp4")
        sys.exit(1)
    
    # Build command
    cmd_parts = [sys.executable, script]
    if needs_video:
        cmd_parts.append(video_path)
    cmd_parts.extend(extra_args)
    
    # Execute
    import subprocess
    try:
        result = subprocess.run(cmd_parts, check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\n\nWorkflow interrupted by user")
        sys.exit(130)


def main():
    parser = argparse.ArgumentParser(
        description="Resume video recap workflow from any checkpoint",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive menu
  python resume_workflow.py /path/to/video.mp4
  
  # Resume from specific point
  python resume_workflow.py /path/to/video.mp4 --from 3
  
  # With additional options
  python resume_workflow.py /path/to/video.mp4 --from 2 --duration 45 --voice shimmer
        """
    )
    parser.add_argument("video_path", nargs="?", help="Path to the video file")
    parser.add_argument("--from", dest="from_step", type=int, choices=range(1, 7),
                       help="Resume from specific step (1-6)")
    parser.add_argument("--status", action="store_true",
                       help="Show checkpoint status and exit")
    
    # Parse known args to allow passing through to child scripts
    args, unknown = parser.parse_known_args()
    
    if args.status:
        print_checkpoint_status()
        suggested_step, reason = get_suggested_starting_point()
        print(f"💡 Suggested starting point: Step {suggested_step}")
        print(f"   Reason: {reason}\n")
        sys.exit(0)
    
    # Show checkpoint status
    print_checkpoint_status()
    
    # Get choice
    if args.from_step:
        choice = args.from_step
        print(f"▶️  Resuming from step {choice}\n")
    else:
        choice = show_menu()
    
    if choice == 0:
        print("Exiting...")
        sys.exit(0)
    
    # Run workflow
    run_workflow(choice, args.video_path, unknown)


if __name__ == "__main__":
    main()

