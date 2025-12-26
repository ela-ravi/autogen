# AI Video Transcription & Recap Generator

An intelligent video transcription, translation, and recap generation system powered by OpenAI Whisper, GPT-4, and Autogen agents.

## Features

### 1. **Video Transcription** 🎤
- Automatically transcribes video/audio files using OpenAI Whisper
- Generates timestamped transcripts
- Supports multiple video formats

### 2. **Translation** 🌍
- Translates transcripts to any language using GPT-4
- Maintains timestamp information
- Preserves subtitle formatting

### 3. **AI-Powered Recap Generation** ✨ *NEW*
- Generates engaging 30-second video recaps
- AI analyzes transcripts to identify key moments
- Suggests optimal clip timings for maximum impact
- Creates professional recap text

### 4. **Automatic Video Clip Extraction** 🎬 *NEW*
- Extracts clips from original video based on AI suggestions
- Combines clips into a seamless recap video
- Preserves video quality and audio sync

## Architecture

### Autogen Agents
- **Chatbot Agent**: AI assistant that orchestrates the workflow
- **User Proxy Agent**: Executes functions and manages tasks
- **Recap Generator**: Analyzes transcripts to create compelling recaps

### Core Functions
1. `recognize_transcript_from_video()` - Speech-to-text transcription
2. `translate_transcript()` - Multi-language translation
3. `generate_recap()` - AI-powered recap generation with clip suggestions
4. `extract_video_clips()` - Video clip extraction and composition

## Installation

### Prerequisites
- Python 3.8+
- FFmpeg (required by moviepy)

### Install FFmpeg
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from: https://ffmpeg.org/download.html
```

### Install Python Dependencies
```bash
cd transcribe_video
pip install -r requirements.txt
```

### Environment Setup
Create a `.env` file in the `transcribe_video/` directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
model=gpt-4
```

## Usage

### Run the Application
```bash
cd transcribe_video
python transcribe.py
```

### Interactive Prompts
1. **Video path**: Path to your video file (e.g., `/path/to/video.mp4`)
2. **Source language**: Original language (e.g., `English`)
3. **Target language**: Translation language (e.g., `Tamil`, `French`, `Spanish`)
4. **Create recap**: Type `yes` to generate a 30-second recap video

### Example Workflow
```
What is your target video path?: /Users/ravi/Downloads/my_video.mp4
What is the source language? (i.e. English): English
What is destination language? (i.e. French): Spanish
Do you want to create a 30-second recap video? (yes/no): yes
```

## Output Files

### Standard Transcription
- `transcription.txt` - Original timestamped transcript
- `{language}_transcription.txt` - Translated transcript

### Recap Generation (when enabled)
- `recap_data.json` - AI-generated clip suggestions and metadata
- `recap_text.txt` - Recap narration text
- `recap_video.mp4` - Final combined recap video

### Example Output Structure
```
transcription.txt:
0s to 5.0s: I can't believe I did this!
5.0s to 7.0s: I can't believe I did this.
...

recap_data.json:
{
  "recap_text": "An emotional journey of...",
  "clip_timings": [
    {"start": 0, "end": 5, "reason": "Opening statement"},
    {"start": 19, "end": 22, "reason": "Key emotional moment"}
  ],
  "total_duration": 30
}
```

## How It Works

### Recap Generation Process
1. **Transcription**: Whisper model transcribes the video with timestamps
2. **AI Analysis**: GPT-4 analyzes the full transcript to identify key moments
3. **Clip Selection**: AI selects optimal clips totaling ~30 seconds
4. **Video Extraction**: MoviePy extracts and combines the selected clips
5. **Output**: Final recap video with seamless transitions

### AI Recap Selection Criteria
- Most impactful or interesting moments
- Natural flow when combined
- Representative of overall tone/message
- Emotional peaks and key statements

## Technical Details

### Dependencies
- `pyautogen` - Multi-agent orchestration framework
- `openai-whisper` - Speech recognition model
- `openai` - GPT-4 API client
- `moviepy` - Video editing and clip extraction
- `python-dotenv` - Environment variable management

### Models Used
- **Whisper Small**: Fast, accurate speech recognition
- **GPT-4**: Intelligent recap generation and translation

## Project Structure
```
autogen/
├── .gitignore
├── .venv/
├── README.md
└── transcribe_video/
    ├── .env                     # API keys (not tracked in git)
    ├── functions.py             # Core functions
    ├── transcribe.py            # Main entry point
    ├── requirements.txt         # Dependencies
    ├── scripts/                 # Autogen working directory
    ├── transcription.txt        # Generated transcript
    ├── {lang}_transcription.txt # Translated transcript
    ├── recap_data.json          # Recap metadata
    ├── recap_text.txt           # Recap narration
    └── recap_video.mp4          # Final recap video
```

## Troubleshooting

### MoviePy Import Error
If you get `ModuleNotFoundError: No module named 'moviepy.editor'`:
```bash
pip install moviepy==1.0.3
```

### FFmpeg Not Found
Install FFmpeg (see Installation section above)

### API Rate Limits
GPT-4 API calls are rate-limited. For long videos with many clips, processing may take time.

### Memory Issues
For large video files, ensure sufficient RAM. The Whisper "small" model requires ~2GB RAM.

## Security Notes
- Never commit `.env` files to version control
- Keep API keys secure
- Use `.gitignore` to exclude sensitive files

## License
MIT License

## Contributing
Contributions welcome! Please submit issues and pull requests.

---

**Built with ❤️ using OpenAI Whisper, GPT-4, Autogen, and MoviePy**

