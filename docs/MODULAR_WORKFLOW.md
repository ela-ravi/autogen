# Modular Workflow Documentation

## 🎯 Overview

The video recap generation system has been completely refactored into a **modular, chainable workflow**. Each step is now:
- ✅ **Independent** - Can be run separately
- ✅ **Chainable** - Outputs feed into next step
- ✅ **Debuggable** - Easy to rerun failed steps
- ✅ **CLI-friendly** - All scripts accept command-line arguments

## 📁 Project Structure

```
autogen/
├── run_recap_workflow.py          # 🌟 Master script (runs all steps)
├── test_modular_workflow.py       # Test suite
│
└── transcribe_video/
    ├── modules/                    # Core logic (reusable functions)
    │   ├── __init__.py
    │   ├── transcription.py        # Video transcription & translation
    │   ├── video_processing.py     # Recap generation & clip extraction
    │   └── audio_processing.py     # TTS & audio-video merging
    │
    ├── scripts/                    # CLI scripts (one per step)
    │   ├── 01_transcribe.py
    │   ├── 02_translate.py
    │   ├── 03_generate_recap.py
    │   ├── 04_extract_clips.py
    │   ├── 05_remove_audio.py
    │   ├── 06_generate_tts.py
    │   └── 07_merge_audio_video.py
    │
    └── output/                     # Generated files
        ├── transcriptions/
        ├── videos/
        └── audio/
```

---

## 🚀 Quick Start

### Option 1: Run Complete Workflow (Recommended)

```bash
python run_recap_workflow.py /path/to/video.mp4
```

**With options:**
```bash
# With translation
python run_recap_workflow.py /path/to/video.mp4 --translate English Tamil

# Custom duration and voice
python run_recap_workflow.py /path/to/video.mp4 --duration 45 --voice shimmer

# Remove original audio before adding narration
python run_recap_workflow.py /path/to/video.mp4 --remove-original-audio
```

### Option 2: Run Individual Steps

Perfect for debugging or rerunning specific steps:

```bash
# Step 1: Transcribe video
python transcribe_video/scripts/01_transcribe.py /path/to/video.mp4

# Step 2: Translate (optional)
python transcribe_video/scripts/02_translate.py \
  transcribe_video/output/transcriptions/transcription.txt \
  English Tamil

# Step 3: Generate AI recap suggestions
python transcribe_video/scripts/03_generate_recap.py \
  transcribe_video/output/transcriptions/transcription.txt

# Step 4: Extract and merge clips
python transcribe_video/scripts/04_extract_clips.py \
  /path/to/video.mp4 \
  transcribe_video/output/transcriptions/recap_data.json

# Step 5: Remove audio (optional)
python transcribe_video/scripts/05_remove_audio.py \
  transcribe_video/output/videos/recap_video.mp4

# Step 6: Generate TTS audio
python transcribe_video/scripts/06_generate_tts.py \
  transcribe_video/output/transcriptions/recap_text.txt

# Step 7: Merge audio with video
python transcribe_video/scripts/07_merge_audio_video.py \
  transcribe_video/output/videos/recap_video.mp4 \
  transcribe_video/output/audio/recap_narration.mp3
```

---

## 📋 Detailed Step Documentation

### Step 1: Transcribe Video

**Script:** `01_transcribe.py`

**What it does:**
- Extracts audio from video
- Transcribes using Whisper
- Creates timestamped transcript

**Usage:**
```bash
python transcribe_video/scripts/01_transcribe.py <video_path> [--model <size>]
```

**Options:**
- `--model`: Whisper model size (tiny, base, small, medium, large) - default: small
- `--output-dir`: Custom output directory

**Output:**
- `transcribe_video/output/transcriptions/transcription.txt`
- `transcribe_video/output/transcriptions/transcription.json`

**Example:**
```bash
python transcribe_video/scripts/01_transcribe.py /path/to/video.mp4 --model medium
```

---

### Step 2: Translate Transcription

**Script:** `02_translate.py`

**What it does:**
- Translates transcription using GPT-4
- Preserves timestamps

**Usage:**
```bash
python transcribe_video/scripts/02_translate.py <transcription_file> <source_lang> <target_lang>
```

**Output:**
- `transcribe_video/output/transcriptions/<target_lang>_transcription.txt`

**Example:**
```bash
python transcribe_video/scripts/02_translate.py \
  transcribe_video/output/transcriptions/transcription.txt \
  English Spanish
```

---

### Step 3: Generate Recap Suggestions

**Script:** `03_generate_recap.py`

**What it does:**
- Analyzes transcript with GPT-4
- Suggests optimal clip timings
- Generates recap narration text

**Usage:**
```bash
python transcribe_video/scripts/03_generate_recap.py <transcription_file> [--duration <seconds>]
```

**Options:**
- `--duration`: Target recap duration in seconds (default: 30)

**Output:**
- `transcribe_video/output/transcriptions/recap_data.json`
- `transcribe_video/output/transcriptions/recap_text.txt`

**Example:**
```bash
python transcribe_video/scripts/03_generate_recap.py \
  transcribe_video/output/transcriptions/transcription.txt \
  --duration 45
```

---

### Step 4: Extract and Merge Clips

**Script:** `04_extract_clips.py`

**What it does:**
- Extracts clips based on AI suggestions
- Concatenates into single video
- Adjusts to exactly target duration

**Usage:**
```bash
python transcribe_video/scripts/04_extract_clips.py <video_path> <recap_data_file> [--duration <seconds>]
```

**Output:**
- `transcribe_video/output/videos/recap_video.mp4`

**Example:**
```bash
python transcribe_video/scripts/04_extract_clips.py \
  /path/to/video.mp4 \
  transcribe_video/output/transcriptions/recap_data.json \
  --duration 45
```

---

### Step 5: Remove Audio (Optional)

**Script:** `05_remove_audio.py`

**What it does:**
- Removes audio track from video
- Useful for adding clean narration

**Usage:**
```bash
python transcribe_video/scripts/05_remove_audio.py <input_video> [<output_video>]
```

**Output:**
- `<input_video>_no_audio.mp4` (or custom path)

**Example:**
```bash
python transcribe_video/scripts/05_remove_audio.py \
  transcribe_video/output/videos/recap_video.mp4
```

---

### Step 6: Generate TTS Audio

**Script:** `06_generate_tts.py`

**What it does:**
- Generates TTS audio from recap text
- Uses OpenAI TTS API

**Usage:**
```bash
python transcribe_video/scripts/06_generate_tts.py <recap_text_file> [--model <model>] [--voice <voice>]
```

**Options:**
- `--model`: tts-1 or tts-1-hd (default: tts-1)
- `--voice`: alloy, echo, fable, onyx, nova, shimmer (default: nova)
- `--duration`: Target duration (default: 30)

**Output:**
- `transcribe_video/output/audio/recap_narration.mp3`

**Example:**
```bash
python transcribe_video/scripts/06_generate_tts.py \
  transcribe_video/output/transcriptions/recap_text.txt \
  --model tts-1-hd --voice shimmer
```

---

### Step 7: Merge Audio with Video

**Script:** `07_merge_audio_video.py`

**What it does:**
- Merges TTS audio with recap video
- Adjusts audio duration to match video
- Creates final output

**Usage:**
```bash
python transcribe_video/scripts/07_merge_audio_video.py <video_path> <audio_path> [<output_path>]
```

**Output:**
- `transcribe_video/output/videos/recap_video_with_narration.mp4`

**Example:**
```bash
python transcribe_video/scripts/07_merge_audio_video.py \
  transcribe_video/output/videos/recap_video.mp4 \
  transcribe_video/output/audio/recap_narration.mp3
```

---

## 🔧 Debugging & Troubleshooting

### When a Step Fails

1. **Identify the failed step** from error message
2. **Fix the issue** (check API keys, file paths, etc.)
3. **Rerun only that step** with the appropriate script

**Example:** If Step 6 (TTS) fails:
```bash
# Just rerun Step 6
python transcribe_video/scripts/06_generate_tts.py \
  transcribe_video/output/transcriptions/recap_text.txt

# Then continue with Step 7
python transcribe_video/scripts/07_merge_audio_video.py \
  transcribe_video/output/videos/recap_video.mp4 \
  transcribe_video/output/audio/recap_narration.mp3
```

### Common Issues

**Issue:** "File not found"
**Solution:** Check that the output from the previous step exists. Run steps in order.

**Issue:** "OpenAI API error"
**Solution:** Check your `.env` file has correct `OPENAI_API_KEY`

**Issue:** "Import error"
**Solution:** Make sure you're running scripts from the project root directory

---

## 💰 Cost Optimization

### Run Only What You Need

**Scenario 1:** Only need transcription
```bash
python transcribe_video/scripts/01_transcribe.py /path/to/video.mp4
# Stop here - no API costs for GPT-4 or TTS
```

**Scenario 2:** Regenerate TTS with different voice
```bash
# Skip expensive steps, just regenerate audio
python transcribe_video/scripts/06_generate_tts.py \
  transcribe_video/output/transcriptions/recap_text.txt \
  --voice shimmer

python transcribe_video/scripts/07_merge_audio_video.py \
  transcribe_video/output/videos/recap_video.mp4 \
  transcribe_video/output/audio/recap_narration.mp3
```

**Scenario 3:** Different recap duration
```bash
# Rerun from Step 3 (recap generation)
python transcribe_video/scripts/03_generate_recap.py \
  transcribe_video/output/transcriptions/transcription.txt \
  --duration 60

# Continue from Step 4
python transcribe_video/scripts/04_extract_clips.py \
  /path/to/video.mp4 \
  transcribe_video/output/transcriptions/recap_data.json \
  --duration 60

# And so on...
```

---

## 📦 Module API Reference

### `modules.transcription`

```python
from modules.transcription import transcribe_video, translate_transcription

# Transcribe video
output_file = transcribe_video(
    video_path="/path/to/video.mp4",
    output_dir="output/transcriptions",
    model_size="small"
)

# Translate transcription
translated_file = translate_transcription(
    input_file="output/transcriptions/transcription.txt",
    source_lang="English",
    target_lang="Tamil",
    output_dir="output/transcriptions"
)
```

### `modules.video_processing`

```python
from modules.video_processing import (
    generate_recap_suggestions,
    extract_and_merge_clips,
    remove_audio_from_video
)

# Generate recap
recap_data_file = generate_recap_suggestions(
    transcription_file="output/transcriptions/transcription.txt",
    target_duration=30
)

# Extract clips
recap_video = extract_and_merge_clips(
    video_path="/path/to/video.mp4",
    recap_data_file="output/transcriptions/recap_data.json",
    target_duration=30
)

# Remove audio
silent_video = remove_audio_from_video(
    input_video="output/videos/recap_video.mp4"
)
```

### `modules.audio_processing`

```python
from modules.audio_processing import generate_tts_audio, merge_audio_with_video

# Generate TTS
audio_file = generate_tts_audio(
    recap_text_file="output/transcriptions/recap_text.txt",
    target_duration=30,
    tts_model="tts-1",
    tts_voice="nova"
)

# Merge audio with video
final_video = merge_audio_with_video(
    video_path="output/videos/recap_video.mp4",
    audio_path="output/audio/recap_narration.mp3"
)
```

---

## ✅ Testing

Run the test suite to verify everything is working:

```bash
python test_modular_workflow.py
```

This will:
- ✅ Test all module imports
- ✅ Verify file structure
- ✅ Show usage examples

---

## 🎓 Best Practices

1. **Run master script for new videos**
   ```bash
   python run_recap_workflow.py /path/to/video.mp4
   ```

2. **Use individual scripts for debugging**
   - Saves API costs
   - Faster iteration
   - Easy to test specific steps

3. **Keep intermediate files**
   - Don't delete `output/` directory
   - Allows rerunning steps without reprocessing

4. **Use appropriate Whisper model**
   - `tiny`: Fastest, lowest quality
   - `small`: Good balance (default)
   - `medium`: Better accuracy
   - `large`: Best quality, slowest

5. **Check output files after each step**
   - Verify transcription quality
   - Review AI recap suggestions
   - Preview recap video before adding audio

---

## 📊 Workflow Diagram

```
Input Video
    │
    ▼
┌─────────────────────┐
│ 1. Transcribe       │──► transcription.txt
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ 2. Translate        │──► tamil_transcription.txt
│    (optional)       │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ 3. Generate Recap   │──► recap_data.json
│    (AI Analysis)    │──► recap_text.txt
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ 4. Extract Clips    │──► recap_video.mp4
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ 5. Remove Audio     │──► recap_video_no_audio.mp4
│    (optional)       │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ 6. Generate TTS     │──► recap_narration.mp3
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ 7. Merge Audio      │──► recap_video_with_narration.mp4
└─────────────────────┘
    │
    ▼
Final Output 🎉
```

---

## 🚀 Ready to Use!

Your modular workflow is ready. Get started with:

```bash
python run_recap_workflow.py /path/to/your/video.mp4
```

For individual step control, see the examples above!

