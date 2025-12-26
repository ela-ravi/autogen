# Complete Workflow Scripts Documentation

## Overview

You now have **3 ways** to run the video recap generation workflow:

### Option 1: Complete Workflow (Recommended) 🌟
```bash
python run_complete_workflow.py
```
**What it does:**
1. Runs `transcribe.py` (transcription + translation + recap + clip extraction)
2. Generates TTS audio narration
3. Merges audio with video
4. Shows complete summary

**Use when:** Starting from scratch with a new video

---

### Option 2: Post-Processing Only 🎵
```bash
python post_process_recap.py
```
**What it does:**
1. Generates TTS audio narration from existing recap text
2. Merges audio with existing recap video

**Use when:** You already ran `transcribe.py` and just need the audio steps

---

### Option 3: Original Transcribe Script 📝
```bash
python transcribe_video/transcribe.py
```
**What it does:**
1. Transcribes video
2. Translates transcript (optional)
3. Generates recap suggestions
4. Extracts and combines video clips

**Use when:** You only need transcription and video extraction (no TTS audio)

---

## Complete Workflow Breakdown

### Full Process (Option 1)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. TRANSCRIPTION WORKFLOW (transcribe.py)                   │
├─────────────────────────────────────────────────────────────┤
│   ├─ Transcribe video with Whisper                          │
│   ├─ Translate transcript (if requested)                    │
│   ├─ Generate AI recap suggestions with GPT-4               │
│   └─ Extract and combine video clips                        │
│                                                              │
│ 2. TTS AUDIO GENERATION                                      │
│   └─ Generate narration audio with OpenAI TTS               │
│                                                              │
│ 3. AUDIO-VIDEO MERGE                                         │
│   ├─ Extend audio with silence to match video duration      │
│   └─ Create final video with narration                      │
└─────────────────────────────────────────────────────────────┘
```

### Generated Files

```
transcribe_video/output/
├── transcriptions/
│   ├── transcription.txt           # Original transcription with timestamps
│   ├── recap_data.json             # AI recap suggestions (clips + timings)
│   ├── recap_text.txt              # Narration text for TTS
│   └── [lang]_transcription.txt    # Translated transcript (if requested)
│
├── videos/
│   ├── recap_video.mp4             # 30s recap (no narration)
│   └── recap_video_with_narration.mp4  # 🌟 FINAL OUTPUT (with TTS)
│
└── audio/
    └── recap_narration_timed.mp3   # TTS audio narration
```

---

## Detailed Script Information

### 1. `run_complete_workflow.py`

**Purpose:** Master orchestration script that runs everything

**Features:**
- Runs `transcribe.py` via subprocess
- Automatically detects if recap was created
- Generates TTS audio
- Merges audio with video
- Shows comprehensive summary of all generated files

**Example Output:**
```
╔════════════════════════════════════════════════════════════╗
║          COMPLETE VIDEO RECAP GENERATION WORKFLOW          ║
╚════════════════════════════════════════════════════════════╝

STEP 1: RUNNING TRANSCRIPTION & RECAP GENERATION WORKFLOW
[Interactive prompts for video path, languages, etc.]
✅ Transcription workflow completed!

STEP 2: GENERATING TTS AUDIO NARRATION
✅ Audio generated!

STEP 3: MERGING AUDIO WITH VIDEO
✅ Final video created!

🎉 WORKFLOW COMPLETED SUCCESSFULLY!
```

---

### 2. `post_process_recap.py`

**Purpose:** Quick post-processing for existing recap videos

**Features:**
- Checks prerequisites (recap_video.mp4, recap_text.txt, recap_data.json)
- Generates TTS audio from recap text
- Merges audio with video
- Extends audio with silence to match 30s video duration

**Use Cases:**
- You already ran `transcribe.py`
- You want to regenerate audio with different voice/model
- The workflow was interrupted after video creation

**Example Output:**
```
╔══════════════════════════════════════════════════════════╗
║        RECAP VIDEO POST-PROCESSING                       ║
╚══════════════════════════════════════════════════════════╝

Checking prerequisites...
✅ Found recap_video
✅ Found recap_text
✅ Found recap_data

STEP 1: GENERATING TTS AUDIO NARRATION
✅ Audio generation complete!

STEP 2: MERGING AUDIO WITH VIDEO
✅ Post-processing completed!
```

---

### 3. `transcribe_video/transcribe.py`

**Purpose:** Original Autogen-based workflow

**Features:**
- Interactive prompts for video path and languages
- Autogen agents for task orchestration
- Whisper for transcription
- GPT-4 for translation and recap generation
- MoviePy for video clip extraction

**Interactive Prompts:**
```
What is your target video path?: /path/to/video.mp4
What is the source language?: English
What is destination language?: Tamil
Do you want to create a 30-second recap video? (yes/no): yes
```

**Note:** This script stops after creating `recap_video.mp4` (no TTS audio)

---

### 4. `continue_workflow.py` (Utility Script)

**Purpose:** Resume workflow from clip extraction (for debugging)

**Features:**
- Skips transcription and recap generation
- Only runs: clip extraction → TTS → merge
- Useful for saving API costs during testing

**Usage:**
```bash
python continue_workflow.py "/path/to/video.mp4"
```

---

## Quick Reference

### First Time Running
```bash
python run_complete_workflow.py
```

### Already Have Recap Video
```bash
python post_process_recap.py
```

### Only Need Transcription (No TTS)
```bash
python transcribe_video/transcribe.py
```

### Resume After Failure
```bash
python continue_workflow.py "/path/to/video.mp4"
```

---

## Cost Optimization Tips 💰

1. **Use `post_process_recap.py`** when you already have the recap video
   - Saves Whisper API costs (transcription)
   - Saves GPT-4 API costs (translation + recap generation)
   - Only pays for TTS (much cheaper)

2. **Use `continue_workflow.py`** during development/testing
   - Skips redundant API calls
   - Reuses existing transcription and recap data

3. **Full workflow** only when starting fresh
   - First time processing a video
   - Need to regenerate everything from scratch

---

## Troubleshooting

### Issue: "recap_video.mp4 not found"
**Solution:** Run `transcribe.py` first to create the recap video

### Issue: "recap_text.txt not found"
**Solution:** The recap generation step failed. Check OpenAI API key and quota

### Issue: "Audio is shorter than video"
**Solution:** Normal behavior - script automatically pads with silence

### Issue: Path errors / File not found
**Solution:** All scripts now use absolute paths - should work from any directory

---

## Next Steps

✅ Your workflow is complete and working!

**To process a new video:**
```bash
python run_complete_workflow.py
```

**To regenerate audio for existing recap:**
```bash
python post_process_recap.py
```

All scripts are ready to use! 🚀

