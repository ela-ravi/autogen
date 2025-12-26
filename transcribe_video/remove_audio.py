#!/usr/bin/env python3
"""
Remove Audio from Recap Video

This script removes the audio track from the recap video.
Useful for:
- Adding custom background music
- Adding voiceover narration
- Creating silent video for social media
- Reducing file size

Usage:
    python remove_audio.py                          # Remove audio from recap_video.mp4
    python remove_audio.py input.mp4                # Remove audio from specific file
    python remove_audio.py input.mp4 output.mp4     # Specify both input and output
"""

import os
import sys
from functions import remove_audio_from_recap


def main():
    """Main function to handle command-line arguments and remove audio."""
    
    print("╔══════════════════════════════════════════════════════════╗")
    print("║         RECAP VIDEO - AUDIO REMOVAL TOOL                ║")
    print("╚══════════════════════════════════════════════════════════╝\n")
    
    # Default values
    input_video = "recap_video.mp4"
    output_video = "recap_video_no_audio.mp4"
    
    # Parse command-line arguments
    if len(sys.argv) >= 2:
        input_video = sys.argv[1]
        
        # Generate default output name based on input
        base_name = os.path.splitext(input_video)[0]
        output_video = f"{base_name}_no_audio.mp4"
    
    if len(sys.argv) >= 3:
        output_video = sys.argv[2]
    
    # Check if input file exists
    if not os.path.exists(input_video):
        print(f"❌ Error: Input video not found: {input_video}\n")
        print("Usage:")
        print("  python remove_audio.py                          # Use default recap_video.mp4")
        print("  python remove_audio.py input.mp4                # Specify input file")
        print("  python remove_audio.py input.mp4 output.mp4     # Specify both files")
        sys.exit(1)
    
    # Show file info
    input_size = os.path.getsize(input_video) / (1024 * 1024)  # MB
    print(f"📹 Input video:  {input_video} ({input_size:.2f} MB)")
    print(f"📁 Output video: {output_video}")
    print()
    
    # Confirm action
    confirm = input("Do you want to proceed? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Operation cancelled.")
        sys.exit(0)
    
    print("\n⏳ Processing...")
    print("-" * 60)
    
    # Remove audio
    result = remove_audio_from_recap(input_video, output_video)
    
    print("-" * 60)
    print(f"\n✅ {result}\n")
    
    # Show next steps
    print("💡 Next steps:")
    print(f"   • Add background music: Use video editing software")
    print(f"   • Add voiceover: Use audio editing tools")
    print(f"   • Upload to social media: {output_video} is ready!")
    print()


def quick_remove():
    """Quick mode - remove audio without confirmation."""
    if not os.path.exists("recap_video.mp4"):
        print("❌ Error: recap_video.mp4 not found")
        print("   Please generate a recap video first using:")
        print("   python transcribe.py")
        sys.exit(1)
    
    print("Removing audio from recap_video.mp4...")
    result = remove_audio_from_recap()
    print(result)


if __name__ == "__main__":
    # Check for --quick flag
    if len(sys.argv) == 2 and sys.argv[1] == "--quick":
        quick_remove()
    else:
        try:
            main()
        except KeyboardInterrupt:
            print("\n\n⚠️  Operation cancelled by user")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

