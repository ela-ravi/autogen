#!/usr/bin/env python3
"""
Repository Reorganization Script

This script reorganizes the autogen repository into a proper structure:
- docs/ for all documentation
- transcribe_video/scripts/ for utility scripts
- transcribe_video/output/ for generated files
"""

import os
import shutil
from pathlib import Path

def create_directory_structure():
    """Create the new directory structure"""
    
    directories = [
        "docs",
        "transcribe_video/scripts",
        "transcribe_video/output",
        "transcribe_video/output/transcriptions",
        "transcribe_video/output/videos",
        "transcribe_video/output/audio",
    ]
    
    print("Creating directory structure...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✅ {directory}/")
    
    return True


def move_documentation():
    """Move all documentation files to docs/"""
    
    print("\nMoving documentation files...")
    
    # Root level docs
    root_docs = [
        "IMPLEMENTATION_SUMMARY.md",
        "CODE_CHANGES.md"
    ]
    
    for doc in root_docs:
        if os.path.exists(doc):
            shutil.move(doc, f"docs/{doc}")
            print(f"  ✅ {doc} → docs/")
    
    # transcribe_video docs
    tv_docs = [
        "RECAP_WORKFLOW.md",
        "AUDIO_MERGE_FIX.md",
        "AUDIO_TIMESTRETCH_FIX.md",
        "SPEEDX_FIX.md",
        "MOVIEPY_1.0.3_FIX.md",
        "SOLUTION_COMPLETE.md"
    ]
    
    for doc in tv_docs:
        src = f"transcribe_video/{doc}"
        if os.path.exists(src):
            shutil.move(src, f"docs/{doc}")
            print(f"  ✅ {doc} → docs/")
    
    return True


def move_scripts():
    """Move utility scripts to transcribe_video/scripts/"""
    
    print("\nMoving utility scripts...")
    
    scripts = [
        "demo.py",
        "remove_audio.py",
        "generate_tts_audio.py",
        "analyze_sync.py",
        "test_speedx.py",
        "test_audio_merge.py"
    ]
    
    for script in scripts:
        src = f"transcribe_video/{script}"
        if os.path.exists(src):
            shutil.move(src, f"transcribe_video/scripts/{script}")
            print(f"  ✅ {script} → scripts/")
    
    return True


def move_outputs():
    """Move generated output files to transcribe_video/output/"""
    
    print("\nMoving generated output files...")
    
    # Transcription files
    transcriptions = [
        "transcription.txt",
        "Tamil_transcription.txt",
        "ta_transcription.txt",
        "recap_data.json",
        "recap_text.txt"
    ]
    
    for file in transcriptions:
        src = f"transcribe_video/{file}"
        if os.path.exists(src):
            shutil.move(src, f"transcribe_video/output/transcriptions/{file}")
            print(f"  ✅ {file} → output/transcriptions/")
    
    # Video files
    videos = [
        "recap_video.mp4",
        "recap_video_with_narration.mp4",
        "recap_video_no_audio.mp4"
    ]
    
    for file in videos:
        src = f"transcribe_video/{file}"
        if os.path.exists(src):
            shutil.move(src, f"transcribe_video/output/videos/{file}")
            print(f"  ✅ {file} → output/videos/")
    
    # Audio files
    audio = [
        "recap_narration_timed.mp3",
        "recap_narration.mp3",
        "temp-audio.m4a"
    ]
    
    for file in audio:
        src = f"transcribe_video/{file}"
        if os.path.exists(src):
            shutil.move(src, f"transcribe_video/output/audio/{file}")
            print(f"  ✅ {file} → output/audio/")
    
    return True


def update_gitignore():
    """Update .gitignore with new paths"""
    
    print("\nUpdating .gitignore...")
    
    gitignore_additions = """
# Output directories (generated files)
transcribe_video/output/
!transcribe_video/output/.gitkeep

# Keep structure
transcribe_video/output/transcriptions/.gitkeep
transcribe_video/output/videos/.gitkeep
transcribe_video/output/audio/.gitkeep
"""
    
    with open(".gitignore", "a") as f:
        f.write(gitignore_additions)
    
    print("  ✅ .gitignore updated")
    
    return True


def create_gitkeep_files():
    """Create .gitkeep files to preserve directory structure in git"""
    
    print("\nCreating .gitkeep files...")
    
    dirs = [
        "transcribe_video/output/transcriptions",
        "transcribe_video/output/videos",
        "transcribe_video/output/audio"
    ]
    
    for directory in dirs:
        gitkeep = f"{directory}/.gitkeep"
        Path(gitkeep).touch()
        print(f"  ✅ {gitkeep}")
    
    return True


def create_readme_files():
    """Create README files for each directory"""
    
    print("\nCreating README files...")
    
    # docs/README.md
    with open("docs/README.md", "w") as f:
        f.write("""# Documentation

This directory contains all project documentation.

## Files

- `README.md` - Project overview and setup guide (root level)
- `IMPLEMENTATION_SUMMARY.md` - Task completion summary
- `CODE_CHANGES.md` - Detailed code changes reference
- `RECAP_WORKFLOW.md` - Recap generation workflow
- `AUDIO_MERGE_FIX.md` - Audio merging fix documentation
- `AUDIO_TIMESTRETCH_FIX.md` - Time-stretching solution
- `SPEEDX_FIX.md` - speedx compatibility fix
- `MOVIEPY_1.0.3_FIX.md` - MoviePy 1.0.3 compatibility
- `SOLUTION_COMPLETE.md` - Complete solution guide
""")
    print("  ✅ docs/README.md")
    
    # transcribe_video/scripts/README.md
    with open("transcribe_video/scripts/README.md", "w") as f:
        f.write("""# Utility Scripts

This directory contains utility scripts for the transcription system.

## Scripts

- `demo.py` - Interactive demo script
- `remove_audio.py` - Remove audio from videos
- `generate_tts_audio.py` - Generate TTS narration
- `analyze_sync.py` - Analyze audio/video sync
- `test_speedx.py` - Test speedx functionality
- `test_audio_merge.py` - Test audio merging

## Usage

```bash
cd scripts
python demo.py /path/to/video.mp4
python generate_tts_audio.py --merge
python analyze_sync.py
```
""")
    print("  ✅ transcribe_video/scripts/README.md")
    
    # transcribe_video/output/README.md
    with open("transcribe_video/output/README.md", "w") as f:
        f.write("""# Output Directory

This directory contains all generated output files.

## Structure

```
output/
├── transcriptions/   # Transcript files (.txt, .json)
├── videos/          # Generated video files (.mp4)
└── audio/           # Generated audio files (.mp3, .m4a)
```

## Files

### Transcriptions
- `transcription.txt` - Original timestamped transcript
- `{language}_transcription.txt` - Translated transcripts
- `recap_data.json` - AI-generated clip suggestions
- `recap_text.txt` - Recap narration text

### Videos
- `recap_video.mp4` - Combined clip recap video
- `recap_video_with_narration.mp4` - Final video with TTS audio
- `recap_video_no_audio.mp4` - Video without audio

### Audio
- `recap_narration_timed.mp3` - TTS narration audio
- `temp-audio.m4a` - Temporary audio files

## Note

These files are gitignored. They are generated during runtime.
""")
    print("  ✅ transcribe_video/output/README.md")
    
    return True


def main():
    """Main reorganization function"""
    
    print("=" * 70)
    print("REPOSITORY REORGANIZATION")
    print("=" * 70)
    print()
    
    # Confirm
    response = input("This will reorganize the repository structure. Continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Aborted.")
        return
    
    print()
    
    try:
        # Execute reorganization steps
        create_directory_structure()
        move_documentation()
        move_scripts()
        move_outputs()
        create_gitkeep_files()
        create_readme_files()
        update_gitignore()
        
        print()
        print("=" * 70)
        print("✅ REORGANIZATION COMPLETE!")
        print("=" * 70)
        print()
        print("New structure:")
        print("""
autogen/
├── README.md
├── .gitignore
├── docs/                          ← All documentation
│   ├── README.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── CODE_CHANGES.md
│   └── ...
└── transcribe_video/
    ├── functions.py               ← Core functions
    ├── transcribe.py              ← Main script
    ├── requirements.txt
    ├── .env
    ├── scripts/                   ← Utility scripts
    │   ├── README.md
    │   ├── demo.py
    │   ├── generate_tts_audio.py
    │   └── ...
    └── output/                    ← Generated files (gitignored)
        ├── README.md
        ├── transcriptions/
        ├── videos/
        └── audio/
        """)
        
        print("\n⚠️  Important: Update import paths in your scripts!")
        print("   Example: from scripts.generate_tts_audio import ...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

