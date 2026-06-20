#!/usr/bin/env python3
"""
Quick test script to verify emotion integration in recap generation.

Run this after setting up Google Cloud to test:
  1. Transcription with emotions
  2. Recap generation with emotion weighting
  3. Comparison of clips selected with vs without emotions
"""

import os
import sys
import json
from pathlib import Path

def test_emotion_recap_integration():
    """Test the full emotion-integrated recap pipeline."""

    print("\n" + "="*70)
    print("Testing Emotion Integration in Recap Generation")
    print("="*70 + "\n")

    # Check for test video
    test_video = None
    test_dirs = [
        "test_videos",
        "test_data",
        "samples",
        "output/test"
    ]

    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            for ext in [".mp4", ".mov", ".mkv", ".avi"]:
                for f in Path(test_dir).glob(f"*{ext}"):
                    test_video = str(f)
                    break
            if test_video:
                break

    if not test_video:
        print("⚠️  No test video found. Expected in:")
        for d in test_dirs:
            print(f"   - {d}/*.mp4")
        print("\nTo test, provide a short video (30-60s) or use AUDIO_EMOTIONS_QUICKSTART.md")
        return False

    print(f"✓ Found test video: {test_video}\n")

    # Import modules
    try:
        from modules.transcription import transcribe_with_optional_emotions
        from modules.video_processing import generate_recap_suggestions
        print("✓ Imported transcription and video processing modules\n")
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

    try:
        from app.processing.emotion_analysis import analyze_audio_emotions
        print("✓ Emotion analysis module available\n")
    except ImportError:
        print("⚠️  Emotion analysis not imported (may be in different location)\n")

    # Test 1: Transcription only (BASIC tier)
    print("-" * 70)
    print("TEST 1: Transcription Only (BASIC/FREE tier)")
    print("-" * 70)
    try:
        trans1, emo1 = transcribe_with_optional_emotions(
            test_video,
            include_emotions=False
        )
        print(f"✓ Transcription complete: {trans1}")
        print(f"  Emotions: {emo1}\n")
    except Exception as e:
        print(f"✗ Transcription failed: {e}\n")
        return False

    # Test 2: Transcription with emotions (PREMIUM tier)
    print("-" * 70)
    print("TEST 2: Transcription + Emotions (PREMIUM tier)")
    print("-" * 70)
    try:
        trans2, emo2 = transcribe_with_optional_emotions(
            test_video,
            include_emotions=True
        )
        print(f"✓ Transcription complete: {trans2}")
        print(f"✓ Emotions complete: {emo2}\n")
    except Exception as e:
        print(f"⚠️  Emotion analysis failed (check Google Cloud setup): {e}\n")
        print("   This is expected if Google Cloud is not configured.")
        print("   See onetime-setup/README.md for setup instructions.\n")
        emo2 = None

    # Test 3: Recap WITHOUT emotion weighting
    print("-" * 70)
    print("TEST 3: Recap Generation (WITHOUT emotion weighting)")
    print("-" * 70)
    try:
        recap1 = generate_recap_suggestions(
            transcription_file=trans1,
            target_duration=30,
            emotions_file=None
        )

        with open(recap1, "r") as f:
            recap1_data = json.load(f)

        clips1 = recap1_data.get("clip_timings", [])
        text1 = recap1_data.get("recap_text", "")

        print(f"✓ Recap generated: {recap1}")
        print(f"  Clips selected: {len(clips1)}")
        print(f"  Narration words: {len(text1.split())}")
        print(f"  Sample clips: {clips1[:2] if clips1 else 'None'}\n")
    except Exception as e:
        print(f"✗ Recap generation failed: {e}\n")
        return False

    # Test 4: Recap WITH emotion weighting (if emotions available)
    if emo2:
        print("-" * 70)
        print("TEST 4: Recap Generation (WITH emotion weighting)")
        print("-" * 70)
        try:
            recap2 = generate_recap_suggestions(
                transcription_file=trans2,
                target_duration=30,
                emotions_file=emo2
            )

            with open(recap2, "r") as f:
                recap2_data = json.load(f)

            clips2 = recap2_data.get("clip_timings", [])
            text2 = recap2_data.get("recap_text", "")
            emotions_used = recap2_data.get("emotions_used", False)

            print(f"✓ Recap with emotions generated: {recap2}")
            print(f"  Emotions used: {emotions_used}")
            print(f"  Clips selected: {len(clips2)}")
            print(f"  Narration words: {len(text2.split())}")
            print(f"  Sample clips: {clips2[:2] if clips2 else 'None'}\n")

            # Compare
            print("-" * 70)
            print("COMPARISON: With vs Without Emotions")
            print("-" * 70)
            print(f"Clips WITHOUT emotions: {len(clips1)}")
            print(f"Clips WITH emotions:    {len(clips2)}")
            print(f"Difference:             {len(clips2) - len(clips1):+d}\n")

            print(f"Narration WITHOUT emotions ({len(text1.split())} words):")
            print(f"  {text1[:100]}...\n")

            print(f"Narration WITH emotions ({len(text2.split())} words):")
            print(f"  {text2[:100]}...\n")

        except Exception as e:
            print(f"⚠️  Emotion-weighted recap failed: {e}\n")

    # Summary
    print("=" * 70)
    print("✅ TESTS COMPLETE")
    print("=" * 70)
    print("\nResults:")
    print(f"  ✓ Transcription (BASIC): {trans1}")
    print(f"  ✓ Recap without emotions: {recap1}")
    if emo2:
        print(f"  ✓ Transcription (PREMIUM): {trans2}")
        print(f"  ✓ Recap with emotions: {recap2}")
    else:
        print("  ⚠️  Emotions not tested (Google Cloud not configured)")

    print("\nNext Steps:")
    print("  1. Review output/transcriptions/ for transcript and emotion files")
    print("  2. Compare recap_data.json with/without emotions")
    print("  3. See AUDIO_EMOTIONS_RECAP_INTEGRATION.md for detailed usage")
    print("  4. Follow Task #5: Integrate into backend pipeline\n")

    return True


if __name__ == "__main__":
    success = test_emotion_recap_integration()
    sys.exit(0 if success else 1)
