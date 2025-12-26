# Autogen Projects

This repository contains various Autogen-based projects.

## 📦 Projects

### 🎬 [Video Transcription & AI Recap Generator](./transcribe_video/)

AI-powered video processing system for transcription, translation, and automated recap generation.

**Quick Start:**
```bash
cd transcribe_video
python run_recap_workflow.py /path/to/video.mp4
```

**Features:**
- Video transcription with OpenAI Whisper
- Multi-language translation
- AI-powered recap generation
- Smart clip selection
- Text-to-speech narration
- Complete modular workflow

**Documentation:** See [transcribe_video/README.md](./transcribe_video/README.md)

---

## 🚀 Getting Started

Each project is self-contained in its own directory with:
- Complete documentation
- Dependencies list
- Example usage
- Test suites

Navigate to the project directory and follow its README.

---

## 📂 Repository Structure

```
autogen/
├── transcribe_video/      # Video processing & AI recaps
│   ├── README.md          # Complete documentation
│   ├── modules/           # Core logic
│   ├── scripts/           # CLI tools
│   └── docs/              # Detailed guides
│
└── [future projects]/     # Other Autogen projects
```

---

## 🛠️ Setup

Each project has its own setup. For example, for `transcribe_video`:

```bash
cd transcribe_video
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

---

## 📚 Documentation

Each project has comprehensive documentation:
- Main README with quick start
- Detailed workflow guides
- API references
- Troubleshooting guides

---

## 🤝 Contributing

Each project is modular and independent. Contributions welcome!

---

## 📄 License

See individual project directories for licensing information.
