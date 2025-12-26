# Repository Reorganization Plan

## Current Structure (Messy) ❌

```
autogen/
├── README.md
├── IMPLEMENTATION_SUMMARY.md
├── CODE_CHANGES.md
├── .gitignore
└── transcribe_video/
    ├── functions.py
    ├── transcribe.py
    ├── requirements.txt
    ├── .env
    ├── demo.py
    ├── remove_audio.py
    ├── generate_tts_audio.py
    ├── analyze_sync.py
    ├── test_speedx.py
    ├── test_audio_merge.py
    ├── RECAP_WORKFLOW.md
    ├── AUDIO_MERGE_FIX.md
    ├── AUDIO_TIMESTRETCH_FIX.md
    ├── SPEEDX_FIX.md
    ├── MOVIEPY_1.0.3_FIX.md
    ├── SOLUTION_COMPLETE.md
    ├── transcription.txt
    ├── Tamil_transcription.txt
    ├── recap_data.json
    ├── recap_text.txt
    ├── recap_video.mp4
    ├── recap_narration_timed.mp3
    └── recap_video_with_narration.mp4
```

**Problems:**
- ❌ 8+ scripts mixed with core files
- ❌ 6+ documentation files in wrong location  
- ❌ 8+ generated output files tracked/visible
- ❌ No clear organization
- ❌ Hard to find specific files

---

## New Structure (Clean) ✅

```
autogen/
├── README.md                              # Project overview
├── .gitignore                             # Git ignore rules
│
├── docs/                                  # 📚 All Documentation
│   ├── README.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── CODE_CHANGES.md
│   ├── RECAP_WORKFLOW.md
│   ├── AUDIO_MERGE_FIX.md
│   ├── AUDIO_TIMESTRETCH_FIX.md
│   ├── SPEEDX_FIX.md
│   ├── MOVIEPY_1.0.3_FIX.md
│   └── SOLUTION_COMPLETE.md
│
└── transcribe_video/
    ├── functions.py                       # Core logic
    ├── transcribe.py                      # Main entry point
    ├── requirements.txt                   # Dependencies
    ├── .env                               # Config (gitignored)
    │
    ├── scripts/                           # 🛠️ Utility Scripts
    │   ├── README.md
    │   ├── demo.py
    │   ├── remove_audio.py
    │   ├── generate_tts_audio.py
    │   ├── analyze_sync.py
    │   ├── test_speedx.py
    │   └── test_audio_merge.py
    │
    └── output/                            # 📁 Generated Files (gitignored)
        ├── README.md
        ├── transcriptions/
        │   ├── .gitkeep
        │   ├── transcription.txt
        │   ├── Tamil_transcription.txt
        │   ├── recap_data.json
        │   └── recap_text.txt
        ├── videos/
        │   ├── .gitkeep
        │   ├── recap_video.mp4
        │   └── recap_video_with_narration.mp4
        └── audio/
            ├── .gitkeep
            └── recap_narration_timed.mp3
```

**Benefits:**
- ✅ Clear separation of concerns
- ✅ Easy to find documentation
- ✅ Utility scripts organized
- ✅ Generated files separated
- ✅ Professional structure
- ✅ Better for Git/version control

---

## File Categories

### Core Files (Root of transcribe_video/)
**Purpose:** Essential files for the main functionality
```
functions.py       # Core transcription/translation/recap logic
transcribe.py      # Main Autogen agent orchestration
requirements.txt   # Python dependencies
.env               # API keys and configuration
```

### Documentation (docs/)
**Purpose:** All project documentation
```
README.md                      # Main project documentation
IMPLEMENTATION_SUMMARY.md      # Task completion summary
CODE_CHANGES.md               # Code changes reference
RECAP_WORKFLOW.md             # Workflow diagrams
AUDIO_MERGE_FIX.md            # Fix documentation
AUDIO_TIMESTRETCH_FIX.md      # Time-stretching guide
SPEEDX_FIX.md                 # speedx compatibility
MOVIEPY_1.0.3_FIX.md          # Version compatibility
SOLUTION_COMPLETE.md          # Complete solution guide
```

### Utility Scripts (transcribe_video/scripts/)
**Purpose:** Helper tools and utilities
```
demo.py                    # Interactive demo
remove_audio.py            # Audio removal tool
generate_tts_audio.py      # TTS audio generator
analyze_sync.py            # Audio/video sync analyzer
test_speedx.py             # speedx function test
test_audio_merge.py        # Audio merge test
```

### Output Files (transcribe_video/output/)
**Purpose:** All generated/temporary files
```
transcriptions/            # Text outputs
  ├── transcription.txt           # Original transcript
  ├── {lang}_transcription.txt    # Translations
  ├── recap_data.json             # AI suggestions
  └── recap_text.txt              # Recap narration

videos/                    # Video outputs
  ├── recap_video.mp4                    # Clip compilation
  └── recap_video_with_narration.mp4     # Final video

audio/                     # Audio outputs
  └── recap_narration_timed.mp3   # TTS narration
```

---

## Migration Steps

### Automated (Recommended):
```bash
cd /Volumes/Development/Practise/autogen
python reorganize.py
```

### Manual Steps:
```bash
# 1. Create directories
mkdir -p docs
mkdir -p transcribe_video/scripts
mkdir -p transcribe_video/output/{transcriptions,videos,audio}

# 2. Move documentation
mv IMPLEMENTATION_SUMMARY.md docs/
mv CODE_CHANGES.md docs/
mv transcribe_video/*.md docs/

# 3. Move scripts
mv transcribe_video/demo.py transcribe_video/scripts/
mv transcribe_video/remove_audio.py transcribe_video/scripts/
mv transcribe_video/generate_tts_audio.py transcribe_video/scripts/
mv transcribe_video/analyze_sync.py transcribe_video/scripts/
mv transcribe_video/test_*.py transcribe_video/scripts/

# 4. Move outputs
mv transcribe_video/*.txt transcribe_video/output/transcriptions/
mv transcribe_video/*.json transcribe_video/output/transcriptions/
mv transcribe_video/*.mp4 transcribe_video/output/videos/
mv transcribe_video/*.mp3 transcribe_video/output/audio/

# 5. Create .gitkeep files
touch transcribe_video/output/{transcriptions,videos,audio}/.gitkeep
```

---

## Updated .gitignore

```gitignore
# Output directories (generated files)
transcribe_video/output/
!transcribe_video/output/.gitkeep
!transcribe_video/output/*/
!transcribe_video/output/*/.gitkeep

# Keep directory structure but ignore contents
transcribe_video/output/transcriptions/*
!transcribe_video/output/transcriptions/.gitkeep

transcribe_video/output/videos/*
!transcribe_video/output/videos/.gitkeep

transcribe_video/output/audio/*
!transcribe_video/output/audio/.gitkeep
```

---

## Usage After Reorganization

### Running Scripts:
```bash
# Main transcription (unchanged)
cd transcribe_video
python transcribe.py

# Utility scripts (new location)
python scripts/demo.py /path/to/video.mp4
python scripts/generate_tts_audio.py --merge
python scripts/analyze_sync.py
python scripts/remove_audio.py
```

### Accessing Outputs:
```bash
# View transcriptions
cat output/transcriptions/transcription.txt
cat output/transcriptions/recap_data.json

# Check videos
ls output/videos/

# Check audio
ls output/audio/
```

### Reading Documentation:
```bash
# View documentation
cat docs/README.md
cat docs/RECAP_WORKFLOW.md
cat docs/MOVIEPY_1.0.3_FIX.md
```

---

## Benefits Summary

| Aspect | Before | After |
|--------|--------|-------|
| File Count (root) | 20+ files | 10 files |
| Documentation | Scattered | docs/ folder |
| Scripts | Mixed | scripts/ folder |
| Outputs | Visible | output/ (gitignored) |
| Findability | Poor | Excellent |
| Professionalism | Low | High |
| Git History | Cluttered | Clean |

---

## Rollback Plan

If you need to undo the reorganization:
```bash
# Automated rollback
python reorganize.py --rollback

# Or manual
mv docs/* .
mv transcribe_video/scripts/* transcribe_video/
mv transcribe_video/output/*/* transcribe_video/
```

---

## Next Steps

1. **Run reorganization:**
   ```bash
   python reorganize.py
   ```

2. **Update imports** (if needed):
   - Update any custom scripts that import from moved files
   - Update documentation links

3. **Test functionality:**
   ```bash
   cd transcribe_video
   python transcribe.py
   python scripts/generate_tts_audio.py --help
   ```

4. **Commit changes:**
   ```bash
   git add .
   git commit -m "Reorganize repository structure"
   ```

---

**Ready to reorganize? Run:** `python reorganize.py`

