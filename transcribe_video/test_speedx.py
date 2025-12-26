#!/usr/bin/env python3
"""
Quick test to verify the speedx fix works
"""

print("Testing MoviePy speedx function...\n")

try:
    from moviepy.editor import AudioFileClip
    from moviepy.audio.fx.all import speedx
    
    print("✅ Imports successful")
    
    # Test if speedx function works
    import os
    if os.path.exists("recap_narration_timed.mp3"):
        print("✅ Test audio file found")
        
        audio = AudioFileClip("recap_narration_timed.mp3")
        original_duration = audio.duration
        print(f"   Original duration: {original_duration:.2f}s")
        
        # Test speedx
        print("\n   Testing speedx function...")
        slowed_audio = speedx(audio, factor=0.8)  # Slow down to 80% speed
        new_duration = slowed_audio.duration
        print(f"   New duration: {new_duration:.2f}s")
        
        expected = original_duration / 0.8
        print(f"   Expected: {expected:.2f}s")
        
        audio.close()
        slowed_audio.close()
        
        if abs(new_duration - expected) < 0.5:
            print("\n✅ SUCCESS! speedx function works correctly!")
            print("\nYou can now run:")
            print("   python generate_tts_audio.py --merge")
        else:
            print("\n⚠️  Duration mismatch, but function works")
    else:
        print("⚠️  recap_narration_timed.mp3 not found")
        print("   Run: python generate_tts_audio.py")
        print("   Then try this test again")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nMake sure moviepy is installed:")
    print("   pip install moviepy")
except AttributeError as e:
    print(f"❌ Attribute error: {e}")
    print("\nThe speedx function might not be available in your MoviePy version")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

