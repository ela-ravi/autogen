# Quick Reference Guide

## 🚀 Most Common Commands

### Run Everything (Recommended for First Time)
```bash
python run_recap_workflow.py /path/to/video.mp4
```

### Run Everything with Translation
```bash
python run_recap_workflow.py /path/to/video.mp4 --translate English Tamil
```

### Run Everything with Custom Options
```bash
python run_recap_workflow.py /path/to/video.mp4 \
  --translate English Spanish \
  --duration 45 \
  --voice shimmer \
  --model medium \
  --remove-original-audio
```

---

## 🔧 Debugging: Run Individual Steps

### Step 1: Transcribe
```bash
python transcribe_video/scripts/01_transcribe.py /path/to/video.mp4
```

### Step 2: Translate (Optional)
```bash
python transcribe_video/scripts/02_translate.py \
  transcribe_video/output/transcriptions/transcription.txt \
  English Tamil
```

### Step 3: Generate Recap
```bash
python transcribe_video/scripts/03_generate_recap.py \
  transcribe_video/output/transcriptions/transcription.txt
```

### Step 4: Extract Clips
```bash
python transcribe_video/scripts/04_extract_clips.py \
  /path/to/video.mp4 \
  transcribe_video/output/transcriptions/recap_data.json
```

### Step 5: Remove Audio (Optional)
```bash
python transcribe_video/scripts/05_remove_audio.py \
  transcribe_video/output/videos/recap_video.mp4
```

### Step 6: Generate TTS
```bash
python transcribe_video/scripts/06_generate_tts.py \
  transcribe_video/output/transcriptions/recap_text.txt
```

### Step 7: Merge Audio+Video
```bash
python transcribe_video/scripts/07_merge_audio_video.py \
  transcribe_video/output/videos/recap_video.mp4 \
  transcribe_video/output/audio/recap_narration.mp3
```

---

## 📂 Output Files

All generated files are in `transcribe_video/output/`:

```
output/
├── transcriptions/
│   ├── transcription.txt          # Original transcript
│   ├── transcription.json         # Transcript with timestamps
│   ├── recap_data.json            # AI clip suggestions
│   ├── recap_text.txt             # Narration text
│   └── tamil_transcription.txt    # Translated (if --translate)
│
├── videos/
│   ├── recap_video.mp4            # Recap without narration
│   └── recap_video_with_narration.mp4  # ⭐ FINAL OUTPUT
│
└── audio/
    └── recap_narration.mp3        # TTS audio
```

---

## 💡 Common Scenarios

### Scenario 1: Regenerate with Different Voice
```bash
# Rerun Step 6 with new voice
python transcribe_video/scripts/06_generate_tts.py \
  transcribe_video/output/transcriptions/recap_text.txt \
  --voice shimmer

# Merge again
python transcribe_video/scripts/07_merge_audio_video.py \
  transcribe_video/output/videos/recap_video.mp4 \
  transcribe_video/output/audio/recap_narration.mp3
```

### Scenario 2: Different Recap Duration
```bash
# Rerun from Step 3 onwards
python transcribe_video/scripts/03_generate_recap.py \
  transcribe_video/output/transcriptions/transcription.txt \
  --duration 60

python transcribe_video/scripts/04_extract_clips.py \
  /path/to/video.mp4 \
  transcribe_video/output/transcriptions/recap_data.json \
  --duration 60

python transcribe_video/scripts/06_generate_tts.py \
  transcribe_video/output/transcriptions/recap_text.txt \
  --duration 60

python transcribe_video/scripts/07_merge_audio_video.py \
  transcribe_video/output/videos/recap_video.mp4 \
  transcribe_video/output/audio/recap_narration.mp3
```

### Scenario 3: Only Transcription (No Recap)
```bash
# Just transcribe
python transcribe_video/scripts/01_transcribe.py /path/to/video.mp4

# Optionally translate
python transcribe_video/scripts/02_translate.py \
  transcribe_video/output/transcriptions/transcription.txt \
  English Spanish
```

---

## 🎛️ All Available Options

### Master Script Options
```
--translate SOURCE TARGET    Translate transcription
--no-translate              Skip translation
--duration N                Recap duration in seconds (default: 30)
--model SIZE                Whisper model: tiny|base|small|medium|large
--tts-model MODEL           TTS model: tts-1|tts-1-hd
--voice VOICE               Voice: alloy|echo|fable|onyx|nova|shimmer
--remove-original-audio     Remove audio before adding narration
```

### Individual Script Options
Each script has `--help` for details:
```bash
python transcribe_video/scripts/01_transcribe.py --help
python transcribe_video/scripts/06_generate_tts.py --help
# etc.
```

---

## 🧪 Testing

Verify everything is working:
```bash
python test_modular_workflow.py
```

---

## 📚 Full Documentation

See `docs/MODULAR_WORKFLOW.md` for complete documentation.

---

## 🆘 Help

### Get Help for Any Script
```bash
python run_recap_workflow.py --help
python transcribe_video/scripts/01_transcribe.py --help
python transcribe_video/scripts/06_generate_tts.py --help
```

### Common Issues

**"File not found"**
- Make sure previous steps completed successfully
- Check `transcribe_video/output/` directory

**"OpenAI API error"**
- Check `.env` file has `OPENAI_API_KEY`
- Verify API quota/credits

**"Import error"**
- Run from project root directory
- Check Python environment has all dependencies

---

## ✅ Quick Checklist

Before running:
- [ ] Video file exists and path is correct
- [ ] `.env` file has `OPENAI_API_KEY`
- [ ] Python virtual environment is activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)

---

## 🎯 Remember

- **Master script** for first run: `python run_recap_workflow.py video.mp4`
- **Individual scripts** for debugging: `python transcribe_video/scripts/XX_*.py`
- **Output location**: `transcribe_video/output/`
- **Final video**: `transcribe_video/output/videos/recap_video_with_narration.mp4`

**Need more help?** Check `docs/MODULAR_WORKFLOW.md`

