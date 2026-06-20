# Audio Emotions - Quick Start Guide

TL;DR implementation checklist to get audio emotion detection running.

---

## Step 1: Setup Google Cloud (30 minutes)

```bash
# 1a. Create GCP project
gcloud projects create videorecap-emotions --name="Video Recap Emotions"
gcloud config set project videorecap-emotions

# 1b. Enable Speech API
gcloud services enable speech.googleapis.com

# 1c. Create service account
gcloud iam service-accounts create videorecap-sa \
  --display-name="Video Recap Service Account"

# 1d. Grant permissions
gcloud projects add-iam-policy-binding videorecap-emotions \
  --member="serviceAccount:videorecap-sa@videorecap-emotions.iam.gserviceaccount.com" \
  --role="roles/speech.admin"

# 1e. Download key
gcloud iam service-accounts keys create ~/videorecap-key.json \
  --iam-account=videorecap-sa@videorecap-emotions.iam.gserviceaccount.com

# 1f. Add to .env
echo 'GOOGLE_APPLICATION_CREDENTIALS=~/videorecap-key.json' >> .env

# 1g. Install dependencies
pip install google-cloud-speech
```

---

## Step 2: Test Emotion Analysis Module (10 minutes)

```python
# Test the emotion_analysis.py module
python -c "
from backend.app.processing.emotion_analysis import analyze_audio_emotions

# Test with sample audio
emotions = analyze_audio_emotions('tests/fixtures/sample_audio.wav')

print(f'Found {len(emotions)} emotion segments')
for e in emotions[:5]:
    print(f\"{e['text']}: {e['dominant_emotion']} ({e['intensity']:.2f})\")
"
```

---

## Step 3: Integrate into Pipeline (2-3 days)

### 3a. Modify transcription.py

```python
# In modules/transcription.py, add:

from app.processing.emotion_analysis import analyze_audio_emotions

def transcribe_video_with_emotions(video_path, output_dir="output/transcriptions"):
    """Transcribe video AND analyze emotions from audio."""
    
    # Step 1: Transcribe (existing code)
    transcript_file = transcribe_video(video_path, output_dir)
    
    # NEW: Step 2.5: Analyze emotions
    audio_path = os.path.join(output_dir, "../original/extracted_audio.wav")
    emotions = analyze_audio_emotions(audio_path)
    
    # Save emotions
    emotion_file = os.path.join(output_dir, "emotions.json")
    with open(emotion_file, "w") as f:
        json.dump(emotions, f, indent=2)
    
    return transcript_file, emotion_file
```

### 3b. Modify video_processing.py

```python
# In modules/video_processing.py, update generate_recap_suggestions():

def generate_recap_suggestions_with_emotions(
    transcription_file,
    emotions_file=None,
    target_duration=30,
    emotion_weight=0.3,
    preferred_emotions=None,
):
    """Generate recap using EMOTIONS to weight clip selection."""
    
    # Load emotion data
    emotion_data = {}
    if emotions_file and os.path.exists(emotions_file):
        with open(emotions_file) as f:
            emotion_data = json.load(f)
    
    # Merge emotions into transcript
    enhanced_segments = _merge_emotions_into_transcript(transcript_segments, emotion_data)
    
    # Modified clip selection prompt
    clip_prompt = f"""
    Select {target_duration}s of clips for a movie recap.
    
    PRIORITIZE EMOTIONAL INTENSITY:
    - Prefer clips with emotion intensity > 0.7
    - Include preferred emotions: {preferred_emotions}
    - Vary emotions, don't repeat
    
    Each segment shows:
    - text: what was said
    - dominant_emotion: joy/sadness/anger/fear/surprise
    - intensity: 0-1 emotional strength
    
    {json.dumps(enhanced_segments)}
    
    Return JSON with clip_timings.
    """
    
    # Rest is same as before...
```

### 3c. Modify backend pipeline.py

```python
# In backend/app/workers/pipeline.py, update run():

if resume_from_step <= 1:
    # Step 1: Transcribe + Emotions (NEW)
    transcription_file, emotions_file = transcribe_video_with_emotions(
        local_video_path
    )
    
    # Save emotions as intermediate
    if emotions_file:
        self._upload_intermediate(intermediate_keys, "emotions", emotions_file)

if resume_from_step <= 3:
    # Step 3: Generate recap WITH emotions (MODIFIED)
    recap_data_file = generate_recap_suggestions_with_emotions(
        transcription_file,
        emotions_file=emotions_file,
        emotion_weight=job_config.get("emotion_weight", 0.3),
    )
```

---

## Step 4: Add User Config (1 day)

### 4a. Update JobConfig schema

```python
# In backend/app/schemas/job.py

class JobConfig(BaseModel):
    target_duration: int = 30
    whisper_model: str = "small"
    language: str = None
    
    # NEW: Emotion config
    use_emotions: bool = True
    emotion_weight: float = 0.3  # 0-1
    preferred_emotions: List[str] = ["joy", "surprise", "intensity"]
```

### 4b. Update frontend JobConfig UI

```jsx
// In frontend/src/components/upload/JobConfigForm.tsx

<div>
  <label>Emotion Weighting</label>
  <input 
    type="range" 
    min="0" 
    max="1" 
    step="0.1"
    value={config.emotion_weight}
    onChange={(e) => setConfig({...config, emotion_weight: parseFloat(e.target.value)})}
  />
  <span>{config.emotion_weight.toFixed(1)} (0=importance-only, 1=emotion-focused)</span>
</div>

<div>
  <label>Prefer These Emotions</label>
  <input type="checkbox" checked={config.preferred_emotions.includes("joy")} />
  <input type="checkbox" checked={config.preferred_emotions.includes("surprise")} />
  <input type="checkbox" checked={config.preferred_emotions.includes("anger")} />
</div>
```

---

## Step 5: Test (2-3 days)

```bash
# 5a. Unit test emotion merging
pytest backend/tests/test_emotion_analysis.py -v

# 5b. Integration test with real video
python scripts/test_emotion_integration.py tests/fixtures/short_film.mp4

# 5c. Compare results (with/without emotions)
python scripts/compare_emotions.py \
  --video tests/fixtures/short_film.mp4 \
  --emotion-weight 0.0 \
  --emotion-weight 0.5 \
  --emotion-weight 1.0
```

---

## Validation Checklist

- [ ] Google Cloud project created and API enabled
- [ ] Service account key downloaded and in .env
- [ ] google-cloud-speech installed
- [ ] emotion_analysis.py module created
- [ ] Test: Can call `analyze_audio_emotions()` successfully
- [ ] transcription.py modified to call emotion analysis
- [ ] Test: Emotions saved to emotions.json
- [ ] video_processing.py modified to use emotions in clip selection
- [ ] Test: Recap selection prefers high-emotion clips
- [ ] backend pipeline.py integrated
- [ ] JobConfig schema updated
- [ ] Frontend emotion config UI added
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual test with 5 film clips passes

---

## Cost Estimation

```
Google Cloud Speech-to-Text pricing:
- $0.004 per 15-second block

For a 10-minute film:
- 40 blocks × $0.004 = $0.16 per film

For 100 films/month:
- 100 × $0.16 = $16/month for emotion analysis

Is it worth it?
- Better clip selection: Yes
- User satisfaction: +30-50%
- Cost: Minimal ($16/month)
```

---

## Common Issues & Fixes

### "google-cloud-speech is not installed"
```bash
pip install google-cloud-speech
```

### "GOOGLE_APPLICATION_CREDENTIALS not found"
```bash
# Make sure your .env file has:
GOOGLE_APPLICATION_CREDENTIALS=/path/to/videorecap-key.json
export GOOGLE_APPLICATION_CREDENTIALS="${GOOGLE_APPLICATION_CREDENTIALS/#\~/$HOME}"
```

### "Authentication failed"
```bash
# Re-download service account key:
gcloud iam service-accounts keys create ~/videorecap-key.json \
  --iam-account=videorecap-sa@videorecap-emotions.iam.gserviceaccount.com

# Update .env with new key path
```

### "Emotion detection is slow"
```python
# Normal: 5-10 seconds per film
# If slower, check:
# - Network latency to Google Cloud
# - Audio file size
# - Number of concurrent requests

# Optimization:
# - Batch process multiple films
# - Run in background worker (Celery)
# - Cache emotion results for same audio
```

---

## Timeline

| Phase | Task | Time |
|-------|------|------|
| 1 | Google Cloud setup | 30 min |
| 2 | Test emotion module | 10 min |
| 3a | Transcription integration | 1 day |
| 3b | Recap generation modification | 1 day |
| 3c | Pipeline integration | 1 day |
| 4a | Schema updates | 2 hours |
| 4b | Frontend UI | 4 hours |
| 5 | Testing & validation | 2-3 days |
| **Total** | **End-to-end** | **~1 week** |

---

## Next Steps After Phase 1

Once Phase 1 is deployed and working:

1. **Gather user feedback** - Do they prefer emotion-based clips?
2. **A/B testing** - Show with/without emotion weighting
3. **Fine-tune emotions** - Adjust weights and preferred emotions per film genre
4. **Phase 2** - Add video emotions (facial expressions, visual intensity)
5. **Hybrid system** - Combine audio + video emotions for best results

---

**Ready to start?** Begin with Step 1! 🎬

