# Resume Scripts

Resume the video recap workflow from any checkpoint to save time and API costs.

## 🎯 Quick Start

### Interactive Menu (Recommended)
```bash
python resume_workflow.py /path/to/video.mp4
```

### Direct Script Usage
```bash
# Resume from specific checkpoint
python resume/02_from_transcription.py /path/to/video.mp4
python resume/03_from_recap_generation.py /path/to/video.mp4
python resume/05_from_tts_generation.py
```

---

## 📋 Available Resume Points

| Script | Skip | Start From | Prerequisites |
|--------|------|------------|---------------|
| `01_from_audio_extraction.py` | Nothing | Audio Extraction | Original video |
| `02_from_transcription.py` | Audio extraction | Transcription | `output/original/extracted_audio.wav` |
| `03_from_recap_generation.py` | Audio + Transcription | AI Recap | `output/transcriptions/transcription.txt` |
| `04_from_clip_extraction.py` | Audio + Transcription + Recap | Clip Extraction | `output/transcriptions/recap_data.json` |
| `05_from_tts_generation.py` | All video steps | TTS Generation | `output/videos/recap_video.mp4` |
| `06_from_audio_merge.py` | Everything | Final Merge | `output/audio/recap_narration.mp3` |

---

## 💡 Use Cases

### 1. Regenerate with Different Voice
Already have the video clips but want a different TTS voice:
```bash
python resume/05_from_tts_generation.py --voice shimmer
```

### 2. Retry Failed Clip Extraction
Transcription and recap exist, but clip extraction failed:
```bash
python resume/04_from_clip_extraction.py /path/to/video.mp4
```

### 3. Change Recap Duration
Want a 45-second recap instead of 30:
```bash
python resume/03_from_recap_generation.py /path/to/video.mp4 --duration 45
```

### 4. Use Existing Audio
Already extracted audio from the video:
```bash
python resume/02_from_transcription.py /path/to/video.mp4 --use-existing-audio output/original/extracted_audio.wav
```

### 5. Quick Remixing
Have everything, just want to merge again with different settings:
```bash
python resume/06_from_audio_merge.py
```

---

## 🔧 Options

### All Scripts Support
```bash
--help              Show detailed help message
```

### Video-Based Scripts (1-4)
```bash
--duration 45       Target recap duration (default: 30)
--voice shimmer     TTS voice (default: nova)
--tts-model tts-1-hd   TTS model (default: tts-1)
--remove-original-audio  Remove original audio before adding narration
```

### Transcription Script (2)
```bash
--model medium      Whisper model size (default: small)
--language en       Source video language
--translate English Tamil  Translate transcript
--use-existing-audio PATH  Path to audio file
```

### Recap Generation Script (3)
```bash
--transcription PATH   Path to transcription file
```

### Clip Extraction Script (4)
```bash
--recap-data PATH   Path to recap data JSON
```

### TTS Generation Script (5)
```bash
--recap-video PATH  Path to recap video
--recap-text PATH   Path to recap text
```

### Audio Merge Script (6)
```bash
--recap-video PATH  Path to recap video
--tts-audio PATH    Path to TTS audio
```

---

## 📊 Check Status

See which files exist and get suggestions:
```bash
python resume_workflow.py --status
```

Example output:
```
CHECKPOINT STATUS
================================================================================
✅ Audio Extraction          output/original/extracted_audio.wav
✅ Transcription             output/transcriptions/transcription.txt
✅ AI Recap Generation       output/transcriptions/recap_data.json
❌ Video Clip Extraction     output/videos/recap_video.mp4
❌ TTS Generation            output/audio/recap_narration.mp3
❌ Final Video               output/videos/recap_video_with_narration.mp4

💡 Suggested starting point: Step 4
   Reason: Resume from Clip Extraction (recap exists)
```

---

## 🎬 Workflow Diagram

```
┌─────────────────────────────────────────────────────────┐
│  1. Audio Extraction                                    │
│     Input: video.mp4                                    │
│     Output: extracted_audio.wav                         │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│  2. Transcription                                       │
│     Input: extracted_audio.wav                          │
│     Output: transcription.txt                           │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│  3. AI Recap Generation                                 │
│     Input: transcription.txt                            │
│     Output: recap_data.json, recap_text.txt             │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│  4. Clip Extraction                                     │
│     Input: video.mp4 + recap_data.json                  │
│     Output: recap_video.mp4                             │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│  5. TTS Generation                                      │
│     Input: recap_text.txt                               │
│     Output: recap_narration.mp3                         │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│  6. Audio Merge                                         │
│     Input: recap_video.mp4 + recap_narration.mp3        │
│     Output: recap_video_with_narration.mp4 ✨          │
└─────────────────────────────────────────────────────────┘
```

**Resume from any step with existing outputs!**

---

## 💰 Cost Savings

Resume scripts help you save on API costs:

| Scenario | Savings |
|----------|---------|
| Regenerate with different voice | Skip $0.10-0.30 GPT-4 recap generation |
| Fix clip extraction | Skip transcription (free) + recap generation |
| Change recap duration | Skip transcription only |
| Merge different audio | Skip all API calls (free operation) |

---

## 🧪 Examples

### Example 1: Complete Workflow, Then Change Voice
```bash
# First run (full workflow)
python run_recap_workflow.py video.mp4

# Regenerate with different voice (saves ~$0.25)
python resume/05_from_tts_generation.py --voice alloy
```

### Example 2: Failed Midway, Resume
```bash
# Original run failed at clip extraction
python run_recap_workflow.py video.mp4
# ... fails during clip extraction

# Resume from that point
python resume/04_from_clip_extraction.py video.mp4
```

### Example 3: Different Recap Lengths
```bash
# Generate 30s recap
python run_recap_workflow.py video.mp4

# Later, generate 60s recap (reuses transcription)
python resume/03_from_recap_generation.py video.mp4 --duration 60
```

### Example 4: Interactive Mode
```bash
python resume_workflow.py video.mp4

# Shows menu:
# 1. From Audio Extraction
# 2. From Transcription
# ...
# 💡 Suggestion: Option 3 - Resume from AI Recap (transcription exists)
#
# Enter your choice (0-6): 3
```

---

## 🔍 Troubleshooting

### "File not found" Error
Make sure the prerequisite files exist:
```bash
python resume_workflow.py --status
```

### Want to Start Fresh
Delete specific output files:
```bash
# Remove everything after transcription
rm output/transcriptions/recap_*.* output/videos/* output/audio/*

# Then resume from recap generation
python resume/from_recap_generation.py video.mp4
```

### Wrong File Paths
Use custom paths:
```bash
python resume/02_from_transcription.py video.mp4 \
  --use-existing-audio /custom/path/audio.wav
```

---

## 📚 See Also

- **[Main README](../README.md)** - Complete documentation
- **[QUICK_REFERENCE](../QUICK_REFERENCE.md)** - Command reference
- **[OUTPUT_PATHS](../OUTPUT_PATHS.md)** - File locations

---

**Ready to resume?**
```bash
python resume_workflow.py /path/to/video.mp4
```

