#!/usr/bin/env python3
"""
Resume Workflow: From Transcription

Use this when you already have extracted audio and want to:
- Skip: Audio extraction
- Start: Transcription → Recap → Clips → TTS → Final Video

Prerequisites:
    - output/original/extracted_audio.wav must exist

Usage:
    python resume/from_transcription.py /path/to/video.mp4 [options]
    
Example:
    python resume/from_transcription.py /path/to/video.mp4 --duration 30
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.transcription import transcribe_video, translate_transcription
from modules.video_processing import generate_recap_suggestions, extract_and_merge_clips, remove_audio_from_video
from modules.audio_processing import generate_tts_audio, merge_audio_with_video


def print_header(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(description="Resume workflow from transcription")
    parser.add_argument("video_path", help="Path to the original video file")
    parser.add_argument("--translate", nargs=2, metavar=("SOURCE", "TARGET"), 
                       help="Translate transcription (e.g., English Tamil)")
    parser.add_argument("--duration", type=int, default=30, help="Target recap duration in seconds")
    parser.add_argument("--model", default="small", help="Whisper model size")
    parser.add_argument("--tts-model", default="tts-1", help="TTS model to use")
    parser.add_argument("--voice", default="nova", help="TTS voice to use")
    parser.add_argument("--language", help="Source video language code")
    parser.add_argument("--remove-original-audio", action="store_true", 
                       help="Remove original audio before adding narration")
    parser.add_argument("--use-existing-audio", default="output/original/extracted_audio.wav",
                       help="Path to existing audio file")
    
    args = parser.parse_args()
    
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*20 + "RESUME FROM TRANSCRIPTION" + " "*33 + "║")
    print("╚" + "="*78 + "╝")
    
    # Check if audio exists
    if not os.path.exists(args.use_existing_audio):
        print(f"\n❌ Error: Audio file not found: {args.use_existing_audio}")
        print("   Run the full workflow first or provide correct path with --use-existing-audio")
        sys.exit(1)
    
    print(f"\n✅ Using existing audio: {args.use_existing_audio}")
    
    try:
        # Step 1: Transcribe using existing audio
        print_header("STEP 1/6: Transcribe Audio")
        transcription_file = transcribe_video(
            video_path=args.video_path,
            model_size=args.model,
            language=args.language,
            existing_audio_path=args.use_existing_audio
        )
        
        # Step 2: Translate (optional)
        if args.translate:
            print_header("STEP 2/6: Translation")
            source_lang, target_lang = args.translate
            transcription_file = translate_transcription(
                transcription_file=transcription_file,
                source_language=source_lang,
                target_language=target_lang
            )
        else:
            print_header("STEP 2/6: Translation (Skipped)")
        
        # Step 3: Generate AI recap
        print_header("STEP 3/6: Generate AI Recap Suggestions")
        recap_data_file = generate_recap_suggestions(
            transcription_file=transcription_file,
            target_duration=args.duration
        )
        
        # Step 4: Extract clips
        print_header("STEP 4/6: Extract and Merge Video Clips")
        recap_video = extract_and_merge_clips(
            video_path=args.video_path,
            recap_data_file=recap_data_file,
            target_duration=args.duration
        )
        
        # Step 5: Remove original audio (optional)
        if args.remove_original_audio:
            print_header("STEP 5/6: Remove Original Audio")
            recap_video = remove_audio_from_video(recap_video)
        else:
            print_header("STEP 5/6: Remove Original Audio (Skipped)")
        
        # Step 6: Generate TTS
        print_header("STEP 6/6: Generate TTS and Merge")
        recap_text_file = recap_data_file.replace("recap_data.json", "recap_text.txt")
        tts_audio = generate_tts_audio(
            recap_text_file=recap_text_file,
            tts_model=args.tts_model,
            tts_voice=args.voice
        )
        
        # Step 7: Merge audio+video
        final_video = merge_audio_with_video(
            video_path=recap_video,
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

