# Video Recap Agent

AI-powered video processing agent for automatic transcription, translation, and recap generation with voiceover narration.

## 🎯 Features

- **Video Transcription** - Extract speech from videos using OpenAI Whisper
- **Multi-language Translation** - Translate transcripts using GPT-4
- **AI-Powered Recaps** - Generate engaging 30-second recaps with AI
- **Smart Clip Selection** - Automatically select best moments from videos
- **Text-to-Speech** - Professional voiceover narration using OpenAI TTS
- **Modular Design** - Run complete workflow or individual steps
- **CLI-Friendly** - All scripts accept command-line arguments
- **Self-Contained** - Everything needed is in this directory

---

## 🚀 Quick Start

> 📖 **New user?** See [SETUP.md](SETUP.md) for detailed setup instructions.

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env  # or use your favorite editor
```

**Required in `.env`:**
```bash
OPENAI_API_KEY=sk-...your-key-here...
```

**Optional in `.env`:**
```bash
model=gpt-4  # GPT model for AI analysis (default: gpt-4)
             # Options: gpt-4, gpt-4-turbo, gpt-4o, gpt-3.5-turbo
```

**Get your API key:** https://platform.openai.com/api-keys

### 3. Run Complete Workflow

```bash
python run_recap_workflow.py /path/to/your/video.mp4
```

That's it! The script will:
1. Transcribe the video
2. Generate AI recap suggestions
3. Extract and merge clips
4. Generate TTS narration
5. Create final video with voiceover

**Output:** `output/videos/recap_video_with_narration.mp4`

### 4. Resume from Checkpoint (Save Time & Costs!)

```bash
# Interactive menu - automatically detects what exists
python resume_workflow.py /path/to/video.mp4

# Or resume from specific point
python resume/03_from_recap_generation.py /path/to/video.mp4  # Skip transcription
python resume/05_from_tts_generation.py --voice shimmer        # Change voice only
```

> 💡 **Save API costs**: Resume from any checkpoint instead of re-running everything!  
> See [resume/README.md](resume/README.md) for details.

---

## 📂 Project Structure

```
video_recap_agent/
├── run_recap_workflow.py      # Master script (runs everything)
├── resume_workflow.py          # Resume from any checkpoint
├── test_modular_workflow.py   # Test suite
├── QUICK_REFERENCE.md          # Command cheat sheet
├── README.md                   # This file
│
├── modules/                    # Core logic
│   ├── transcription.py        # Video → Text
│   ├── video_processing.py     # AI recap & clip extraction
│   └── audio_processing.py     # TTS & audio merging
│
├── scripts/                    # Individual CLI tools
│   ├── 01_transcribe.py
│   ├── 02_translate.py
│   ├── 03_generate_recap.py
│   ├── 04_extract_clips.py
│   ├── 05_remove_audio.py
│   ├── 06_generate_tts.py
│   └── 07_merge_audio_video.py
│
├── resume/                     # Resume from checkpoints
│   ├── README.md               # Resume scripts guide
│   ├── 01_from_audio_extraction.py
│   ├── 02_from_transcription.py
│   ├── 03_from_recap_generation.py
│   ├── 04_from_clip_extraction.py
│   ├── 05_from_tts_generation.py
│   └── 06_from_audio_merge.py
│
└── output/                     # Generated files
    ├── transcriptions/
    ├── videos/
    └── audio/
```

---

## 🔧 Individual Steps

For debugging or custom workflows, run steps individually:

Run steps individually:

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

See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for more examples and options.

---

## ⚙️ Configuration

### Environment Variables (.env)

**Required:**
```bash
OPENAI_API_KEY=sk-...your-key-here...
```
Get your API key from: https://platform.openai.com/api-keys

**Optional:**
```bash
model=gpt-4                    # GPT model for AI analysis
                               # Options: gpt-4, gpt-4-turbo, gpt-4o, gpt-3.5-turbo
                               # Default: gpt-4
```

### What the API is used for:
- **GPT-4**: Analyzing transcripts and generating recap suggestions
- **GPT-4**: Translating transcripts (optional, if you use --translate)
- **Whisper**: Transcribing video audio (runs locally, no API cost)
- **TTS (Text-to-Speech)**: Generating voiceover narration

### Master Script Options

```bash
python run_recap_workflow.py VIDEO_PATH [OPTIONS]

Options:
  --translate SOURCE TARGET    Translate transcription
  --duration SECONDS          Recap duration (default: 30)
  --model SIZE                Whisper model: tiny|base|small|medium|large
  --tts-model MODEL           TTS model: tts-1|tts-1-hd
  --voice VOICE               Voice: alloy|echo|fable|onyx|nova|shimmer
  --language LANG             Language code (e.g., 'en', 'es')
  --pad-with-black            Pad video with black frames to exact duration
  --remove-original-audio     Remove original audio before adding narration
```

### Examples

**Basic usage:**
```bash
python run_recap_workflow.py /path/to/video.mp4
```

**With translation:**
```bash
python run_recap_workflow.py /path/to/video.mp4 --translate English Tamil
```

**Custom options:**
```bash
python run_recap_workflow.py /path/to/video.mp4 \
  --duration 45 \
  --voice shimmer \
  --model medium \
  --language en
```

---

## 🔧 Debugging Step Outputs

During development, you can inspect intermediate outputs from each of the 7 steps to diagnose issues or verify quality.

### Enable Debug Mode

Set `DEBUG=true` in your backend `.env`:
```bash
echo "DEBUG=true" >> backend/.env
docker-compose restart backend
```

### View Intermediate Outputs

**Option 1: API Response** (easiest)
```bash
# Get job with intermediate_keys_detailed
curl http://localhost:8000/api/v1/jobs/{job_id} | jq '.intermediate_keys_detailed'

# Response includes:
{
  "transcription": {
    "key": "jobs/{id}/transcription/transcription.json",
    "name": "transcription",
    "size_mb": 2.3,
    "download_url": "/api/v1/jobs/{id}/debug/transcription"
  },
  ...
}
```

**Option 2: Download via Endpoints**
```bash
# Download each intermediate directly
curl http://localhost:8000/api/v1/jobs/{job_id}/debug/transcription > transcription.json
curl http://localhost:8000/api/v1/jobs/{job_id}/debug/translation > translated.json
curl http://localhost:8000/api/v1/jobs/{job_id}/debug/recap > recap_data.json
curl http://localhost:8000/api/v1/jobs/{job_id}/debug/tts-audio > narration.mp3
curl http://localhost:8000/api/v1/jobs/{job_id}/debug/recap-video > clips.mp4
```

### Understanding Intermediate Files

| Step | File | What it contains | Use case |
|------|------|---|---|
| 1 | `transcription.json` | Timestamped transcript | Verify Whisper accuracy |
| 2 | `translated.json` | Translated transcript | Check GPT translation quality |
| 3 | `recap_data.json` | Clip timings + metadata | Verify which clips were selected |
| 4 | `recap_narration.mp3` | TTS audio file | Check narration voice/quality |
| 5 | `recap_video.mp4` | Merged clips (no audio) | Verify clip selection & timing |
| 7 | `recap_video_with_narration.mp4` | Final output | Download completed video |

### Check Log Metrics

After each step completes, the server logs metrics like:
```bash
# Watch server logs
docker logs autogen-worker-1

# You'll see:
Step 1 complete: Transcription | Size: 2.3MB | Segments: 142 | S3: jobs/{id}/transcription/transcription.json
Step 3 complete: Recap Generation | Size: 45KB | Clips: 8 | Narration: 87 words | S3: jobs/{id}/recap_data/recap_data.json
Step 4 complete: TTS Narration | Size: 1.8MB | Duration: 28.5s | Voice: nova | S3: jobs/{id}/tts_audio/recap_narration.mp3
Step 5 complete: Clip Extraction | Size: 45MB | Duration: 30s | S3: jobs/{id}/recap_video/recap_video.mp4
Step 7 complete: Final Merge | Size: 46MB | Duration: 30s | S3: results/{id}/recap_video_with_narration.mp4
```

### Troubleshooting Failed Steps

```bash
# 1. Get error message
curl http://localhost:8000/api/v1/jobs/{job_id} | jq '.error_message'

# 2. Download intermediate from last successful step
curl http://localhost:8000/api/v1/jobs/{job_id}/debug/recap > last_good_recap.json

# 3. Check server logs
docker logs autogen-backend-1  # FastAPI logs
docker logs autogen-worker-1   # Celery worker logs

# 4. Resume from failed step
curl -X POST http://localhost:8000/api/v1/jobs/{job_id}/resume
# Job resumes from where it failed, using cached outputs
```

---

## 🎯 Claude Code Skills & Tools

### Skills Architecture

| Category | Config File | Source | Scope | Purpose |
|----------|---|---|---|---|
| **External Skills** | `skills-lock.json` | GitHub (Fallow) | Project (committed) | External dependencies |
| **Custom Skills** | `/skills/*.md` | Local (single source) | Both tools | Shared across Claude Code + Cursor |
| **Tool Config** | `.claude/settings.json` | Local | Claude Code only | References `/skills/` |
| **Tool Config** | `.cursor/settings.json` | Local | Cursor only | References `/skills/` |
| **Local Overrides** | `.claude/settings.local.json` | Local (gitignored) | Personal | Individual preferences |

**Single source of truth:** All custom skills defined in `/skills/` and referenced from both `.claude/` and `.cursor/`

### Installed Skills

- **Fallow Skills** (`skills-lock.json`) - [fallow-rs/fallow-skills](https://github.com/fallow-rs/fallow-skills)
- **docs-router** (`.claude/settings.json`) - Route documentation to README.md or separate linked files
- **GitHub MCP** (`.mcp.json`) - Create/manage PRs, view issues, check workflows

### Project-Specific Custom Skills

**docs-router** — Ensures all documentation either lives in `README.md` (inline) or in separate files linked from `README.md`

```bash
# Triggered automatically when documentation is requested
# Workflow: Ask → Route (inline or separate file) → Update README if needed
```

See [`/skills/docs-router.md`](./skills/docs-router.md) for full details.

### Built-in Claude Code Skills

| Skill | Command | Purpose |
|-------|---------|---------|
| Verify | `/verify` | Test changes in browser |
| Code Review | `/code-review` | Review for bugs/quality |
| Simplify | `/simplify` | Refactor for efficiency |
| Security Review | `/security-review` | Security audit |
| Run | `/run` | Start dev server |

---

## 📚 Documentation

- **`SETUP.md`** - Complete setup guide for new users
- **`QUICK_REFERENCE.md`** - Quick command reference with examples
- **`OUTPUT_PATHS.md`** - Output file locations reference
- **`resume/README.md`** - Resume workflow from checkpoints (save time & costs!)
- **`CORE_PROCESS_FLOW.md`** - Detailed step-by-step process with AI models used
- **`DEPLOYMENT.md`** - VPS deployment instructions

---

## 🧪 Testing

```bash
python test_modular_workflow.py
```

---

## 💡 Use Cases

### 1. Create Video Recaps
Generate 30-second highlight reels from longer videos with AI narration.

### 2. Video Transcription
Extract accurate timestamped transcripts from any video.

### 3. Multi-language Subtitles
Transcribe and translate videos to multiple languages.

### 4. Content Repurposing
Extract best moments for social media clips.

### 5. Accessibility
Add narration to videos for accessibility.

---

## 🛠️ Troubleshooting

### "Import errors"
Make sure you're running scripts from the `video_recap_agent` directory:
```bash
cd video_recap_agent
python run_recap_workflow.py /path/to/video.mp4
```

### "OpenAI API error"
Check your `.env` file has a valid `OPENAI_API_KEY`:
```bash
# Open .env file
cat .env

# Should contain:
OPENAI_API_KEY=sk-...your-actual-key...

# If missing or incorrect, get a new key from:
# https://platform.openai.com/api-keys
```

### "File not found"
Previous step may have failed. Run steps individually to identify the issue.

### "Garbled transcription"
Try:
- Specify language: `--language en`
- Use better model: `--model medium` or `--model large`
- Check audio quality of source video

---

## 📦 Dependencies

**Core Libraries:**
- `openai` - GPT-4 for AI analysis, TTS for narration
- `openai-whisper` - Local speech recognition (no API needed)
- `moviepy` - Video processing and editing
- `python-dotenv` - Environment variable management

**Optional:**
- `pydub` - Audio duration analysis

**System Requirements:**
- Python 3.7+
- FFmpeg (for video/audio processing)

Install FFmpeg:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# Download from: https://ffmpeg.org/download.html
```

See `requirements.txt` for complete list.

---

## 🎬 Workflow Diagram

```
Video Input
    ↓
[Transcribe] → transcription.txt
    ↓
[Translate] → tamil_transcription.txt (optional)
    ↓
[AI Recap] → recap_data.json + recap_text.txt
    ↓
[Extract Clips] → recap_video.mp4
    ↓
[Remove Audio] → recap_video_no_audio.mp4 (optional)
    ↓
[Generate TTS] → recap_narration.mp3
    ↓
[Merge Audio] → recap_video_with_narration.mp4 ✨
```

---

## 🤝 Integration

This module is self-contained and can be:
- Used standalone
- Integrated into larger projects
- Deployed as a service
- Extended with custom steps

---

## 📄 License

Part of the Autogen project.

---

## 🆘 Support

For help:
1. Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for commands
2. Check [OUTPUT_PATHS.md](OUTPUT_PATHS.md) for file locations
3. Run `python scripts/<script>.py --help` for script-specific options

---

## ✅ Quick Checklist

Before running:
- [ ] Python 3.7+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with `OPENAI_API_KEY`
- [ ] Video file path is correct

---

**Ready to start? Run:**
```bash
python run_recap_workflow.py /path/to/your/video.mp4
```

🎉 Enjoy your AI-powered video recaps!

