#!/usr/bin/env python3
"""
Master Script: Complete Video Recap Workflow

This script chains all individual steps together for a complete workflow.

Steps:
1. Transcribe video
2. Translate transcription (optional)
3. Generate AI recap suggestions
4. Extract and merge video clips
5. Remove audio from recap (optional)
6. Generate TTS audio narration
7. Merge audio with video

Usage:
    python run_recap_workflow.py <video_path> [options]
    
Example:
    python run_recap_workflow.py /path/to/video.mp4
    python run_recap_workflow.py /path/to/video.mp4 --translate English Tamil --duration 45
    python run_recap_workflow.py /path/to/video.mp4 --no-translate --voice shimmer

Output:
    video_recap_agent/output/videos/recap_video_with_narration.mp4
"""

import sys
import os
import argparse

# Add current directory to path for module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.transcription import transcribe_video, translate_transcription
from modules.video_processing import generate_recap_suggestions, extract_and_merge_clips, remove_audio_from_video
from modules.audio_processing import generate_tts_audio, merge_audio_with_video


def print_header(title):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Complete video recap generation workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Required arguments
    parser.add_argument("video_path", help="Path to input video file")
    
    # Translation options
    parser.add_argument("--translate", nargs=2, metavar=("SOURCE", "TARGET"),
                        help="Translate transcription (e.g., --translate English Tamil)")
    parser.add_argument("--no-translate", action="store_true",
                        help="Skip translation step")
    
    # Recap options
    parser.add_argument("--duration", type=int, default=30,
                        help="Target recap duration in seconds (default: 30)")
    
    # Transcription options
    parser.add_argument("--model", default="small",
                        choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper model size (default: small)")
    
    # TTS options
    parser.add_argument("--tts-model", default="tts-1", choices=["tts-1", "tts-1-hd"],
                        help="TTS model (default: tts-1)")
    parser.add_argument("--voice", default="nova",
                        choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                        help="TTS voice (default: nova)")
    
    # Optional steps
    parser.add_argument("--remove-original-audio", action="store_true",
                        help="Remove original audio from recap video before adding narration")
    parser.add_argument("--pad-with-black", action="store_true",
                        help="Pad video with black frames if shorter than target duration")
    
    # Dry-run options for debugging
    parser.add_argument("--dry-run", action="store_true",
                        help="Skip expensive operations, use existing files (useful for debugging)")
    parser.add_argument("--skip-transcribe", action="store_true",
                        help="Skip transcription, use existing transcription.txt")
    parser.add_argument("--skip-recap", action="store_true",
                        help="Skip AI recap generation, use existing recap_data.json")
    parser.add_argument("--skip-extract", action="store_true",
                        help="Skip video extraction, use existing recap_video.mp4")
    parser.add_argument("--skip-tts", action="store_true",
                        help="Skip TTS generation, use existing audio file")
    
    args = parser.parse_args()
    
    # If dry-run is set, enable all skip flags
    if args.dry_run:
        args.skip_transcribe = True
        args.skip_recap = True
        args.skip_extract = True
        args.skip_tts = True
        print("\n🔍 DRY-RUN MODE: Using existing files, skipping expensive operations\n")
    
    # Validate video file
    if not os.path.exists(args.video_path):
        print(f"❌ Error: Video file not found: {args.video_path}")
        sys.exit(1)
    
    try:
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    COMPLETE VIDEO RECAP WORKFLOW                             ║
║                                                                              ║
║  This will generate a complete video recap with AI narration                ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """)
        
        # Step 1: Transcribe video
        print_header("STEP 1/7: Transcribe Video")
        if args.skip_transcribe:
            transcription_file = os.path.join(
                os.path.dirname(__file__),
                "output/transcriptions/transcription.txt"
            )
            if os.path.exists(transcription_file):
                print(f"⏭️  Skipping transcription, using existing file: {transcription_file}")
            else:
                print(f"❌ Error: Transcription file not found: {transcription_file}")
                print("   Run without --skip-transcribe first to generate it.")
                sys.exit(1)
        else:
            transcription_file = transcribe_video(
                video_path=args.video_path,
                model_size=args.model
            )
        
        # Step 2: Translate (optional)
        if args.translate:
            source_lang, target_lang = args.translate
            print_header(f"STEP 2/7: Translate Transcription ({source_lang} → {target_lang})")
            translate_transcription(
                input_file=transcription_file,
                source_lang=source_lang,
                target_lang=target_lang
            )
        elif not args.no_translate:
            print_header("STEP 2/7: Translation (Skipped - use --translate to enable)")
        
        # Step 3: Generate recap suggestions
        print_header("STEP 3/7: Generate AI Recap Suggestions")
        if args.skip_recap:
            recap_data_file = os.path.join(
                os.path.dirname(__file__),
                "output/transcriptions/recap_data.json"
            )
            if os.path.exists(recap_data_file):
                print(f"⏭️  Skipping recap generation, using existing file: {recap_data_file}")
            else:
                print(f"❌ Error: Recap data file not found: {recap_data_file}")
                print("   Run without --skip-recap first to generate it.")
                sys.exit(1)
        else:
            recap_data_file = generate_recap_suggestions(
                transcription_file=transcription_file,
                target_duration=args.duration
            )
        
        # Step 4: Extract and merge clips
        print_header("STEP 4/7: Extract and Merge Video Clips")
        if args.skip_extract:
            recap_video_file = os.path.join(
                os.path.dirname(__file__),
                "output/videos/recap_video.mp4"
            )
            if os.path.exists(recap_video_file):
                print(f"⏭️  Skipping video extraction, using existing file: {recap_video_file}")
            else:
                print(f"❌ Error: Recap video not found: {recap_video_file}")
                print("   Run without --skip-extract first to generate it.")
                sys.exit(1)
        else:
            recap_video_file = extract_and_merge_clips(
                video_path=args.video_path,
                recap_data_file=recap_data_file,
                target_duration=args.duration,
                pad_with_black=args.pad_with_black
            )
        
        # Step 5: Remove audio (optional)
        if args.remove_original_audio:
            print_header("STEP 5/7: Remove Original Audio from Recap")
            recap_video_file = remove_audio_from_video(
                input_video=recap_video_file
            )
        else:
            print_header("STEP 5/7: Remove Audio (Skipped - use --remove-original-audio to enable)")
        
        # Step 6: Generate TTS audio
        print_header("STEP 6/7: Generate TTS Audio Narration")
        recap_text_file = os.path.join(
            os.path.dirname(recap_data_file),
            "recap_text.txt"
        )
        if args.skip_tts:
            audio_file = os.path.join(
                os.path.dirname(__file__),
                "output/audio/recap_narration.mp3"
            )
            if os.path.exists(audio_file):
                print(f"⏭️  Skipping TTS generation, using existing file: {audio_file}")
            else:
                print(f"❌ Error: Audio file not found: {audio_file}")
                print("   Run without --skip-tts first to generate it.")
                sys.exit(1)
        else:
            audio_file = generate_tts_audio(
                recap_text_file=recap_text_file,
                target_duration=args.duration,
                tts_model=args.tts_model,
                tts_voice=args.voice
            )
        
        # Step 7: Merge audio with video
        print_header("STEP 7/7: Merge Audio with Video")
        final_video = merge_audio_with_video(
            video_path=recap_video_file,
            audio_path=audio_file
        )
        
        # Success!
        print(f"\n{'='*80}")
        print(f"{'='*80}")
        print(f"  🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
        print(f"{'='*80}")
        print(f"{'='*80}\n")
        
        print(f"📹 Final Output: {final_video}")
        
        if os.path.exists(final_video):
            size_mb = os.path.getsize(final_video) / (1024 * 1024)
            print(f"   Size: {size_mb:.2f} MB")
            print(f"   Duration: {args.duration} seconds")
        
        print(f"\n✅ Your video recap with AI narration is ready!")
        print(f"\n📁 All generated files are in: video_recap_agent/output/\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

