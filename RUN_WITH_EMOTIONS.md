# 🎬 Running Video Recap with Emotion Analysis

This guide walks you through running the full application locally with emotion analysis support (PREMIUM tier).

---

## 🚀 Quick Start (5 minutes)

### 1. Terminal 1: Start Backend + Redis + Celery

```bash
cd /Volumes/Development/hallucinotai/videorecap

# Start with Docker Compose (includes PostgreSQL, Redis, Nginx)
docker-compose up -d

# Verify services are running
docker ps | grep -E "postgres|redis|nginx"

# In a new terminal within this directory:
source .venv/bin/activate
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Started server process [12345]
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Terminal 2: Start Celery Worker

```bash
cd /Volumes/Development/hallucinotai/videorecap
source .venv/bin/activate

# Start Celery worker with emotion analysis support
celery -A app.workers.tasks worker --loglevel=info --concurrency=2
```

**Expected output:**
```
Connected to redis://localhost:6379//
celery@hostname ready to accept tasks.
```

### 3. Terminal 3: Start Frontend

```bash
cd /Volumes/Development/hallucinotai/videorecap/frontend
npm run dev
```

**Expected output:**
```
▲ Next.js 14.2.0
✓ Ready in 2.5s
```

### 4. Open in Browser

```
http://localhost:3000
```

---

## 🧪 Testing Emotion Analysis Through UI

### Step 1: Sign Up / Login

1. Go to http://localhost:3000
2. Sign up with email/password or Google OAuth
3. Navigate to Dashboard

### Step 2: Upload Test Video

1. Click **"Upload Video"**
2. Select the test film:
   ```
   test-video/vidssave.com One-Minute Time Machine...mp4
   ```
3. Click **"Upload"**

### Step 3: Configure Job (NEW: Emotion Analysis Option)

**BASIC Tier (Free):**
- ✓ Transcription
- ✗ Emotion analysis
- Cost: $0

**PREMIUM Tier (with emotions):**
- ✓ Transcription
- ✓ Emotion analysis
- ✓ Emotion-weighted clip selection
- ✓ Narration tone matching emotions
- Cost: +$0.02-0.05 per video

### Step 4: Create Job

1. Fill in job config:
   - **Target duration**: 30s
   - **Model**: small (faster) or medium (better)
   - **Include emotions**: **TOGGLE THIS ON** ✅
   - Language, translation (optional)

2. Click **"Create Job"**

### Step 5: Watch Processing

The job will run through these steps:

| Step | BASIC Tier | PREMIUM Tier (with emotions) |
|------|-----------|-----|
| 1 | Transcription | Transcription + Emotion Analysis |
| 2 | Translation (optional) | Translation (optional) |
| 3 | Recap generation | Recap generation + Emotion weighting |
| 4 | TTS narration | TTS narration |
| 5 | Clip extraction | Clip extraction |
| 6 | Audio merge | Audio merge |

**You'll see progress updates:**
```
[Step 1] Transcribing [PREMIUM (with emotion analysis)]...
         Loading Whisper model, then transcribing...

[Step 1] Transcription + emotion analysis complete
         ✓ Extracted 125 transcript segments
         ✓ Analyzed 125 emotion segments (joy, sadness, etc.)

[Step 3] AI analyzing transcription for recap (with emotion weighting)...
         Prioritizing emotionally intense moments (intensity > 0.6)

[Step 3] Recap suggestions generated
         ✓ 12 clips selected (weighted by emotional intensity)
         ✓ Narration written to match emotional arc
```

---

## 📊 Comparing Results: BASIC vs PREMIUM

### Test Both Tiers with Same Video

**Job 1: BASIC (No Emotions)**
```bash
# In UI:
- include_emotions: OFF
- Target: 30s
- Create job
# Wait for completion → recap_video.mp4
```

**Job 2: PREMIUM (With Emotions)**
```bash
# In UI:
- include_emotions: ON
- Target: 30s (same as BASIC)
- Create job
# Wait for completion → recap_video.mp4
```

### Compare the Results

**What to notice:**
1. **Clip selection**: Which moments were chosen?
   - BASIC: Follows transcript order, content importance
   - PREMIUM: Prioritizes emotional peaks (joy, surprise, anger)

2. **Narration**: How does it feel?
   - BASIC: Generic recap tone
   - PREMIUM: Matches emotional journey (uplifting at peaks, measured at valleys)

3. **Pacing**: Is it engaging?
   - BASIC: Even pacing throughout
   - PREMIUM: Varies with emotional intensity

---

## 🔧 Troubleshooting

### "Google Cloud not set up" Error

Emotion analysis requires Google Cloud Speech API. Set up is one-time:

```bash
cd onetime-setup
bash SETUP_COMMANDS.sh
# OR
open GOOGLE_CLOUD_SETUP.md
```

After setup, emotion analysis works automatically for jobs with `include_emotions: true`.

### "Celery task failed" in Job

Check worker logs:

```bash
# Terminal 2 where Celery is running
# Look for error messages or:

celery -A app.workers.tasks inspect active
```

Common issues:
- **"No module named moviepy"**: `pip install moviepy`
- **"Google Cloud credentials not found"**: Ensure `~/.env` or environment has `GOOGLE_APPLICATION_CREDENTIALS` set
- **"OpenAI API key missing"**: Add `OPENAI_API_KEY` to `.env`

### Frontend doesn't show emotion option

1. **Clear browser cache**: DevTools → Clear site data
2. **Rebuild frontend**: `npm run build && npm run dev`
3. **Check console**: F12 → Console for errors

### Video upload fails

1. **Check file format**: MP4, MOV, MKV supported
2. **Check file size**: < 500MB recommended
3. **Check backend logs**: `docker-compose logs backend`

---

## 📝 Job Configuration Reference

```json
{
  "config": {
    "target_duration": 30,
    "whisper_model": "small",  // tiny, base, small, medium, large
    "tts_voice": "nova",       // nova, onyx, alloy, echo, fable, shimmer
    "tts_model": "tts-1",      // tts-1 (fast), tts-1-hd (high quality)
    "language": null,          // en, es, fr, etc. (null = auto-detect)
    "translate_to": null,      // en, es, fr, etc. (null = no translation)
    "pad_with_black": false,   // add black padding between clips
    "include_emotions": false  // NEW: emotion analysis (PREMIUM tier)
  }
}
```

---

## 💰 Pricing Model

| Tier | Features | Cost |
|------|----------|------|
| **BASIC** | Transcription only | $0 |
| **PREMIUM** | + Emotion analysis | +$0.02-0.05/video |

**Example**: 100 videos/month
- BASIC: 100 × $0 = $0
- PREMIUM: 100 × $0.05 = $5
- First 90 days: Free (Google Cloud credits)

---

## 🎯 What Emotion Analysis Does

**For Clip Selection:**
- Identifies peak emotional moments (intensity > 0.6)
- Prioritizes strong emotions: joy, surprise, anger
- Creates more compelling narrative arc

**For Narration:**
- Analyzes emotional tone of selected clips
- Guides LLM to match narration tone
- Uplifting for joy, softer for sadness, intense for anger

**Example Flow:**
```
Video: "This is terrible! Wait, I just got good news!"
    ↓
[Analysis]
- 0-5s: "This is terrible!" → sadness (intensity: 0.8)
- 5-10s: "I got good news!" → joy (intensity: 0.9)
    ↓
[Clip Selection]
- BASIC: Takes both (equal priority)
- PREMIUM: Emphasizes 5-10s joy moment (higher intensity)
    ↓
[Narration]
- BASIC: "Here's a summary of the video."
- PREMIUM: "After a tough moment, comes joy! ..." (tone matches emotions)
```

---

## 📚 Related Docs

- **AUDIO_EMOTIONS_PHASE1.md** - Complete implementation guide
- **AUDIO_EMOTIONS_RECAP_INTEGRATION.md** - Integration architecture
- **onetime-setup/README.md** - Google Cloud setup
- **CLAUDE.md** - Project overview
- **QUICK_REFERENCE.md** - CLI cheatsheet

---

## ✨ Next Steps After Testing UI

1. **Compare results**: Run both BASIC and PREMIUM, compare outputs
2. **Test different videos**: Try with multiple films for consistency
3. **Gather feedback**: Does emotion weighting improve quality?
4. **Deploy to staging**: Push to staging branch for team testing
5. **Move to Task #6**: Update frontend UI for emotion controls

---

**Happy testing! 🎬**
