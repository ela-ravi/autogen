# 🎬 Audio Emotions in Recap Generation (Phase 1)

This guide explains how emotion analysis integrates into the recap generation pipeline and how to use it in your video recap workflow.

---

## 📋 Overview

Emotion analysis enhances **Step 3 (Recap Generation)** by:
- Prioritizing emotionally intense moments in clip selection
- Weighting emotions to improve narrative arc
- Guiding narration tone to match the emotional journey
- Creating more compelling video recaps

---

## 🔄 Data Flow

```
Video
  ↓
[Step 1] Transcription + Emotion Analysis
  ├→ transcription.json (segments with timestamps)
  └→ emotions.json (segment emotions with intensity)
  ↓
[Step 2] Translation (optional)
  ↓
[Step 3] Recap Generation (MODIFIED)
  ├→ Accepts emotions.json
  ├→ Merges emotions into transcript segments
  ├→ Weights clip selection by emotion intensity
  ├→ Guides narration tone to match emotional arc
  └→ recap_data.json (with emotion metadata)
  ↓
[Step 4-7] Clip extraction, audio removal, TTS, merge...
```

---

## 🚀 Usage Examples

### Basic: Transcription Only (FREE TIER)

```python
from modules.transcription import transcribe_with_optional_emotions
from modules.video_processing import generate_recap_suggestions

# Step 1: Transcribe (no emotions)
transcript_file, emotions_file = transcribe_with_optional_emotions(
    video_path="/path/to/film.mp4",
    include_emotions=False  # FREE: no emotion analysis
)

# Step 3: Generate recap (no emotion weighting)
recap_data = generate_recap_suggestions(
    transcription_file=transcript_file,
    target_duration=30,
    emotions_file=None  # No emotion data
)
```

### Premium: Transcription + Emotions (PREMIUM TIER)

```python
from modules.transcription import transcribe_with_optional_emotions
from modules.video_processing import generate_recap_suggestions

# Step 1: Transcribe + analyze emotions
transcript_file, emotions_file = transcribe_with_optional_emotions(
    video_path="/path/to/film.mp4",
    include_emotions=True  # PREMIUM: includes emotion analysis
)

# Step 3: Generate recap with emotion weighting
recap_data = generate_recap_suggestions(
    transcription_file=transcript_file,
    target_duration=30,
    emotions_file=emotions_file  # Enable emotion weighting
)
```

### With Translation

```python
from modules.transcription import transcribe_with_optional_emotions, translate_transcription
from modules.video_processing import generate_recap_suggestions

# Step 1: Transcribe + emotions
transcript_file, emotions_file = transcribe_with_optional_emotions(
    video_path="/path/to/film.mp4",
    include_emotions=True
)

# Step 2: Translate
translated_file = translate_transcription(
    input_file=transcript_file,
    source_lang="English",
    target_lang="Tamil"
)

# Step 3: Generate recap with emotions (uses translated text)
recap_data = generate_recap_suggestions(
    transcription_file=translated_file,
    target_duration=30,
    emotions_file=emotions_file,  # Emotions still used for clip weighting!
    narration_language="Tamil"
)
```

---

## 🧠 How Emotion Weighting Works

### 1. Merging Emotions with Segments

When `emotions_file` is provided, the system:
- Loads emotions.json (word-level or sentence-level emotion segments)
- For each transcript segment, finds the overlapping emotion segment
- Adds emotion metadata: `dominant_emotion`, `intensity`, `confidence`

Example transcript segment WITH emotions:
```json
{
  "start": 45.2,
  "end": 52.5,
  "text": "That was the best moment of my life!",
  "dominant_emotion": "joy",
  "intensity": 0.92,
  "confidence": 0.88,
  "emotions": {
    "joy": 0.92,
    "sadness": 0.05,
    "anger": 0.01,
    "fear": 0.02,
    "surprise": 0.00,
    "disgust": 0.00
  }
}
```

### 2. Clip Selection with Emotion Weighting

The **Call 1** LLM (video editor) is instructed to:
- **Prioritize** segments with high emotional intensity (`intensity > 0.6`)
- **Favor** strong emotions: joy, surprise, anger (narrative drivers)
- **Use emotion intensity** as a tiebreaker when importance is similar

Example instruction in prompt:
```
"When emotion data is present, prioritize segments with high emotional 
intensity (intensity > 0.6) and strong emotions (joy, surprise, anger). 
Use emotion intensity as a tiebreaker when content importance is similar."
```

### 3. Narration Tone Matching

The **Call 2** LLM (scriptwriter) receives:
- **Emotion guidance** extracted from selected clips
- **Dominant emotions** present in the recap (e.g., "joy, surprise")
- Instructions to **match narration tone** to emotional arc

Example guidance:
```
"Emotional arc guidance: The clips contain strong moments of joy, surprise. 
Reflect this emotional journey in your narration tone and pacing."
```

---

## 📊 Emotion Intensities Guide

When selecting clips, the LLM weights segments by intensity:

| Intensity | Characteristic | Use Case |
|-----------|-----------------|----------|
| **0.0-0.3** | Neutral/Flat | Background info, scene transitions |
| **0.3-0.6** | Moderate | Supporting dialogue, context |
| **0.6-0.8** | High | Key emotional moments (prefer for clips) |
| **0.8-1.0** | Peak | Climactic moments (strong priority) |

---

## 🎭 Emotion Types in Narration

The system recognizes 6 base emotions:

| Emotion | Narration Effect |
|---------|-----------------|
| **joy** | Uplifting, energetic tone; faster pacing |
| **sadness** | Softer, slower tone; empathetic delivery |
| **anger** | Intense, powerful tone; emphasis on words |
| **fear** | Cautious, tense tone; measured delivery |
| **surprise** | Excited, engaged tone; dynamic pacing |
| **disgust** | Dismissive tone; emphasis on contrast |

---

## 📁 File Structure

After running `transcribe_with_optional_emotions()` and `generate_recap_suggestions()`:

```
output/
├── transcriptions/
│   ├── transcription.json      (transcript segments)
│   ├── transcription.txt       (human-readable)
│   ├── emotions.json           (emotion segments) ← new with emotions=True
│   ├── recap_data.json         (recap with emotion metadata)
│   └── recap_text.txt
├── original/
│   ├── extracted_audio.wav
│   └── full_transcription.txt
└── videos/
    └── recap_video.mp4         (final merged video)
```

---

## 🔧 Integration with Backends/Workers

### Celery Task Example

```python
from celery import shared_task
from modules.transcription import transcribe_with_optional_emotions
from modules.video_processing import generate_recap_suggestions

@shared_task
def process_video_recap(job_id, video_path, include_emotions=False):
    """Process video with optional emotion analysis."""
    
    # Step 1: Transcribe ± emotions
    transcript_file, emotions_file = transcribe_with_optional_emotions(
        video_path=video_path,
        include_emotions=include_emotions
    )
    
    # Step 3: Generate recap with emotion weighting
    recap_data = generate_recap_suggestions(
        transcription_file=transcript_file,
        target_duration=30,
        emotions_file=emotions_file if include_emotions else None
    )
    
    # Store result in DB/S3
    save_recap_to_storage(job_id, recap_data)
    return recap_data
```

### JobConfig Integration

```python
class JobConfig:
    def __init__(self, user_tier):
        # Determine subscription tier
        self.include_emotions = (user_tier == "premium")

job = JobConfig(user_tier="premium")

# Pipeline uses this flag to enable/disable emotions
transcript_file, emotions_file = transcribe_with_optional_emotions(
    video_path=user_video,
    include_emotions=job.include_emotions
)

recap_data = generate_recap_suggestions(
    transcription_file=transcript_file,
    emotions_file=emotions_file if job.include_emotions else None
)
```

---

## ✅ Verification: Compare With/Without Emotions

After setup, test the quality difference:

```bash
python << 'EOF'
from modules.transcription import transcribe_with_optional_emotions
from modules.video_processing import generate_recap_suggestions
import json

video = "test_film.mp4"

# WITHOUT emotions
trans1, emo1 = transcribe_with_optional_emotions(video, include_emotions=False)
recap1 = generate_recap_suggestions(trans1, emotions_file=None)

# WITH emotions
trans2, emo2 = transcribe_with_optional_emotions(video, include_emotions=True)
recap2 = generate_recap_suggestions(trans2, emotions_file=emo2)

# Compare
with open(recap1) as f:
    r1 = json.load(f)
with open(recap2) as f:
    r2 = json.load(f)

print(f"Without emotions: {len(r1['clip_timings'])} clips")
print(f"With emotions:    {len(r2['clip_timings'])} clips")
print(f"\nWithout: {r1['recap_text'][:100]}...")
print(f"With:    {r2['recap_text'][:100]}...")
EOF
```

---

## 🐛 Troubleshooting

### "emotions_file not found"
```python
# Make sure emotions_file path is correct
recap_data = generate_recap_suggestions(
    transcription_file=transcript_file,
    emotions_file="/path/to/emotions.json"  # Check this path
)
```

### "No clips selected" with emotions
- Emotion data may not overlap well with transcript segments
- Check that emotions.json has non-zero intensity values
- Try without emotions (`emotions_file=None`) to debug

### Narration doesn't match emotion tone
- Emotion intensity may be too low (< 0.5)
- Increase `include_emotions=True` to enable emotion guidance
- Run with emotion data but verify `dominant_emotion` field is populated

---

## 🚀 Next Steps

1. ✅ **Test with sample film** — Use AUDIO_EMOTIONS_QUICKSTART.md test clip
2. **Integrate into backend** — Update pipeline.py workers (Task #5)
3. **Add frontend controls** — Emotion weight slider, preferred_emotions filter (Task #6)
4. **Run full tests** — Unit & integration tests (Task #7)
5. **A/B test with users** — Compare recaps with/without emotions (Task #8)

---

## 📚 Related Files

- **AUDIO_EMOTIONS_PHASE1.md** — Complete Phase 1 implementation guide
- **modules/transcription.py** — Transcription functions
- **modules/video_processing.py** — Recap generation (emotion-aware)
- **app/processing/emotion_analysis.py** — Emotion analysis implementation
- **onetime-setup/** — Google Cloud Speech API setup

---

## 💰 Cost Impact

| Tier | Cost | Features |
|------|------|----------|
| **BASIC** | FREE | Transcription only (Whisper local) |
| **PREMIUM** | +$0.02-0.05/video | Transcription + emotion analysis (Google Cloud) |

Break-even: ~1-2 premium videos to offset Google Cloud credits.

---

**Next**: Run AUDIO_EMOTIONS_QUICKSTART.md to test emotion analysis with a sample clip! 🎬
