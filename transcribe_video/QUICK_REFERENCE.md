# Quick Reference

Fast command reference for common tasks.

## 🚀 Complete Workflow

```bash
# Basic (most common)
python run_recap_workflow.py /path/to/video.mp4

# With translation
python run_recap_workflow.py /path/to/video.mp4 --translate English Tamil

# With custom options
python run_recap_workflow.py /path/to/video.mp4 \
  --duration 45 \
  --voice shimmer \
  --model medium \
  --remove-original-audio
```

---

## 🔧 Individual Steps

```bash
# Step 1: Transcribe
python scripts/01_transcribe.py /path/to/video.mp4

# Step 2: Translate (optional)
python scripts/02_translate.py output/transcriptions/transcription.txt English Tamil

# Step 3: Generate recap
python scripts/03_generate_recap.py output/transcriptions/transcription.txt

# Step 4: Extract clips
python scripts/04_extract_clips.py /path/to/video.mp4 output/transcriptions/recap_data.json

# Step 5: Remove audio (optional)
python scripts/05_remove_audio.py output/videos/recap_video.mp4

# Step 6: Generate TTS
python scripts/06_generate_tts.py output/transcriptions/recap_text.txt

# Step 7: Merge audio+video
python scripts/07_merge_audio_video.py output/videos/recap_video.mp4 output/audio/recap_narration.mp3
```

---

## 📂 Output Files

```
output/
├── original/
│   ├── extracted_audio.wav           # Original audio from video
│   └── full_transcription.txt        # Raw transcription
├── transcriptions/
│   ├── transcription.txt             # Timestamped transcript
│   ├── transcription.json            # JSON format
│   ├── recap_data.json               # AI clip suggestions
│   └── recap_text.txt                # TTS narration script
├── videos/
│   ├── recap_video.mp4               # Recap without narration
│   └── recap_video_with_narration.mp4  # ⭐ FINAL OUTPUT
└── audio/
    └── recap_narration.mp3           # TTS audio
```

See [OUTPUT_PATHS.md](OUTPUT_PATHS.md) for more details.

---

## 💡 Common Scenarios

### Regenerate with Different Voice
```bash
python scripts/06_generate_tts.py output/transcriptions/recap_text.txt --voice shimmer
python scripts/07_merge_audio_video.py output/videos/recap_video.mp4 output/audio/recap_narration.mp3
```

### Different Recap Duration
```bash
python scripts/03_generate_recap.py output/transcriptions/transcription.txt --duration 60
python scripts/04_extract_clips.py /path/to/video.mp4 output/transcriptions/recap_data.json --duration 60
python scripts/06_generate_tts.py output/transcriptions/recap_text.txt --duration 60
python scripts/07_merge_audio_video.py output/videos/recap_video.mp4 output/audio/recap_narration.mp3
```

### Just Transcription (No Recap)
```bash
python scripts/01_transcribe.py /path/to/video.mp4 --model medium
# Output: output/transcriptions/transcription.txt
```

---

## ⚙️ Options

### Master Script Options
```bash
--translate SOURCE TARGET   # Translate (e.g., English Tamil)
--duration SECONDS         # Recap duration (default: 30)
--model SIZE              # Whisper: tiny|base|small|medium|large (default: small)
--tts-model MODEL         # TTS: tts-1|tts-1-hd (default: tts-1)
--voice VOICE             # Voice: alloy|echo|fable|onyx|nova|shimmer (default: nova)
--language CODE           # Language code: en|es|fr|etc
--remove-original-audio   # Remove original audio before adding narration
--pad-with-black          # Pad with black frames to exact duration
--dry-run                 # Skip expensive operations, use existing files
```

### Script-Specific Options
```bash
# Get help for any script
python scripts/01_transcribe.py --help
python scripts/03_generate_recap.py --help
```

---

## 🎯 Available TTS Voices

- **alloy** - Neutral, balanced
- **echo** - Clear, male-leaning
- **fable** - Warm, engaging
- **onyx** - Deep, authoritative
- **nova** - Bright, friendly (default)
- **shimmer** - Soft, pleasant

---

## 📋 Whisper Models

| Model  | Speed    | Quality | Use Case |
|--------|----------|---------|----------|
| tiny   | Fastest  | Basic   | Quick tests |
| base   | Fast     | Good    | Fast processing |
| small  | Balanced | Better  | Default (recommended) |
| medium | Slower   | Great   | High accuracy |
| large  | Slowest  | Best    | Maximum quality |

---

## 🧹 Cleanup

```bash
# Remove all generated files
rm -rf output/transcriptions/* output/videos/* output/audio/* output/original/* output/temp/*

# Remove specific category
rm -rf output/videos/*
```

---

## 🔍 Debugging

### Verify Paths
```bash
python verify_paths.py
```

### Verify Files
```bash
ls -lh output/transcriptions/
ls -lh output/videos/
ls -lh output/audio/
```

---

**Quick Start:**
```bash
python run_recap_workflow.py /path/to/video.mp4
```

See [README.md](README.md) for full documentation.
