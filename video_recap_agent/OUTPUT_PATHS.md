# Output File Paths Reference

Quick reference for where all output files are located.

## 🔑 Prerequisites

Before running, make sure you have:
```bash
# 1. API key configured
cat .env  # Should show: OPENAI_API_KEY=sk-...

# 2. Dependencies installed
pip install -r requirements.txt

# 3. FFmpeg installed
ffmpeg -version
```

---

## All Output Files Location

```
video_recap_agent/output/
```

## File Paths by Type

### 1️⃣ Original Files (From Video)
| File | Path | Description |
|------|------|-------------|
| Extracted Audio | `output/original/extracted_audio.wav` | Audio extracted from input video |
| Full Transcription | `output/original/full_transcription.txt` | Raw transcription without timestamps |

### 2️⃣ Transcription Files
| File | Path | Description |
|------|------|-------------|
| Transcription (Text) | `output/transcriptions/transcription.txt` | Timestamped transcription |
| Transcription (JSON) | `output/transcriptions/transcription.json` | JSON format transcription |
| Translated Text | `output/transcriptions/{lang}_transcription.txt` | Translated version (if applicable) |
| Recap Data | `output/transcriptions/recap_data.json` | AI-generated clip suggestions |
| Recap Text | `output/transcriptions/recap_text.txt` | TTS narration script |

### 3️⃣ Video Files
| File | Path | Description |
|------|------|-------------|
| Recap Video | `output/videos/recap_video.mp4` | Combined clips (no audio) |
| Final Video | `output/videos/recap_video_with_narration.mp4` | **Final output with TTS** |

### 4️⃣ Audio Files
| File | Path | Description |
|------|------|-------------|
| TTS Narration | `output/audio/recap_narration.mp3` | Generated voiceover |

### 5️⃣ Temporary Files
| File | Path | Description |
|------|------|-------------|
| Temp Audio 1 | `output/temp/temp-audio.m4a` | MoviePy temp (video extraction) |
| Temp Audio 2 | `output/temp/merge-temp-audio.m4a` | MoviePy temp (audio merge) |

## Usage in Scripts

### Reading Files
```python
# Import the helper function
from modules import get_output_path

# Get absolute path to any output file
transcription_file = get_output_path("output/transcriptions/transcription.txt")
video_file = get_output_path("output/videos/recap_video.mp4")
audio_file = get_output_path("output/audio/recap_narration.mp3")
```

### Command Line
```bash
# All scripts reference relative to video_recap_agent/
python scripts/03_generate_recap.py output/transcriptions/transcription.txt
python scripts/04_extract_clips.py video.mp4 output/transcriptions/recap_data.json
python scripts/06_generate_tts.py output/transcriptions/recap_text.txt
```

## Quick Access

### View Original Audio
```bash
open output/original/extracted_audio.wav
```

### View Original Transcription
```bash
cat output/original/full_transcription.txt
```

### View Cleaned Transcription
```bash
cat output/transcriptions/transcription.txt
```

### Play Final Video
```bash
open output/videos/recap_video_with_narration.mp4
```

## Clean Up

### Remove All Generated Files
```bash
rm -rf output/transcriptions/* output/videos/* output/audio/* output/original/* output/temp/*
```

### Remove Specific Categories
```bash
# Remove only transcriptions
rm -rf output/transcriptions/*

# Remove only videos
rm -rf output/videos/*

# Remove only audio
rm -rf output/audio/*
```

---

**Last Updated:** December 26, 2025
