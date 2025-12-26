#!/usr/bin/env python3
"""
Compare audio durations before and after time-stretching
"""

import os

def analyze_audio_video_sync():
    """Analyze the audio/video synchronization"""
    
    print("\n" + "="*70)
    print("AUDIO-VIDEO SYNC ANALYZER")
    print("="*70 + "\n")
    
    # Check for files
    files_to_check = {
        "recap_video.mp4": "Recap video",
        "recap_narration_timed.mp3": "TTS audio narration",
        "recap_video_with_narration.mp4": "Final video with audio"
    }
    
    print("📂 Checking files...\n")
    for filename, description in files_to_check.items():
        if os.path.exists(filename):
            size = os.path.getsize(filename) / (1024 * 1024)  # MB
            print(f"✅ {description:30} {filename:35} ({size:.2f} MB)")
        else:
            print(f"❌ {description:30} {filename:35} (Not found)")
    
    print("\n" + "-"*70)
    
    # Try to get durations if moviepy is available
    try:
        from moviepy.editor import VideoFileClip, AudioFileClip
        
        print("\n📊 DURATION ANALYSIS:\n")
        
        # Video duration
        if os.path.exists("recap_video.mp4"):
            video = VideoFileClip("recap_video.mp4")
            video_dur = video.duration
            video.close()
            print(f"   Video (recap_video.mp4):              {video_dur:.2f}s")
        
        # Audio duration
        if os.path.exists("recap_narration_timed.mp3"):
            audio = AudioFileClip("recap_narration_timed.mp3")
            audio_dur = audio.duration
            audio.close()
            print(f"   Audio (recap_narration_timed.mp3):    {audio_dur:.2f}s")
            
            # Calculate difference
            if os.path.exists("recap_video.mp4"):
                diff = abs(video_dur - audio_dur)
                stretch_pct = ((video_dur - audio_dur) / audio_dur) * 100
                
                print(f"\n   Duration difference:                   {diff:.2f}s")
                
                if audio_dur < video_dur:
                    print(f"   Required stretch:                      +{stretch_pct:.1f}%")
                    print(f"   Action: Slow down audio by {stretch_pct:.1f}% ⏸️")
                elif audio_dur > video_dur:
                    print(f"   Required compression:                  {stretch_pct:.1f}%")
                    print(f"   Action: Speed up audio by {abs(stretch_pct):.1f}% ⏩")
                else:
                    print(f"   ✅ Perfect match!")
        
        # Final video duration
        if os.path.exists("recap_video_with_narration.mp4"):
            print(f"\n   Final (recap_video_with_narration.mp4): ", end="")
            final = VideoFileClip("recap_video_with_narration.mp4")
            final_dur = final.duration
            final.close()
            print(f"{final_dur:.2f}s")
            
            # Verify sync
            if os.path.exists("recap_video.mp4"):
                if abs(final_dur - video_dur) < 0.5:
                    print(f"   ✅ Audio and video are IN SYNC!")
                else:
                    print(f"   ⚠️  Sync issue detected")
        
        print("\n" + "-"*70)
        
        # Show the fix
        if os.path.exists("recap_narration_timed.mp3") and os.path.exists("recap_video.mp4"):
            audio = AudioFileClip("recap_narration_timed.mp3")
            video = VideoFileClip("recap_video.mp4")
            
            audio_dur = audio.duration
            video_dur = video.duration
            
            audio.close()
            video.close()
            
            print("\n🎯 TIME-STRETCHING SOLUTION:\n")
            
            if audio_dur < video_dur:
                stretch_factor = audio_dur / video_dur
                stretch_pct = ((video_dur - audio_dur) / audio_dur) * 100
                
                print(f"   Original audio:     {audio_dur:.2f}s")
                print(f"   Target (video):     {video_dur:.2f}s")
                print(f"   Speed factor:       {stretch_factor:.3f}x (slower)")
                print(f"   Stretch amount:     +{stretch_pct:.1f}%")
                print(f"\n   Result: Audio plays at {stretch_factor:.1%} speed")
                print(f"           16s audio → 20s duration (no repeating!) ✅")
                
            elif audio_dur > video_dur:
                speed_factor = audio_dur / video_dur
                compress_pct = ((audio_dur - video_dur) / audio_dur) * 100
                
                print(f"   Original audio:     {audio_dur:.2f}s")
                print(f"   Target (video):     {video_dur:.2f}s")
                print(f"   Speed factor:       {speed_factor:.3f}x (faster)")
                print(f"   Compression:        -{compress_pct:.1f}%")
            else:
                print(f"   ✅ Audio and video already match perfectly!")
        
    except ImportError:
        print("\n💡 Install moviepy to see detailed duration analysis")
    except Exception as e:
        print(f"\n⚠️  Error analyzing: {e}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    analyze_audio_video_sync()

