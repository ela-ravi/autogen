# Absolute Path Fix

## Problem

When running `transcribe.py` from the `transcribe_video` directory, the functions in `functions.py` were using relative file paths like `output/transcriptions/transcript.json`. This caused issues because:

1. The relative paths were resolved from the current working directory (CWD)
2. When running `transcribe.py`, the CWD could be different from where the script expected
3. This resulted in `FileNotFoundError` when trying to read/write files

**Error Example:**
```
Error: Required file not found - [Errno 2] No such file or directory: 'output/transcriptions/recap_data.json'
```

## Solution

Implemented absolute path resolution using a helper function that resolves all paths relative to the location of `functions.py`:

### 1. Added Path Resolution Helper in `functions.py`

```python
import os

# Get the directory where this functions.py file is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Helper function to get absolute paths relative to script directory
def get_output_path(relative_path):
    """Convert relative output path to absolute path"""
    return os.path.join(SCRIPT_DIR, relative_path)
```

### 2. Updated All File Operations

**Before:**
```python
with open("output/transcriptions/transcript.json", "r") as f:
    data = json.load(f)
```

**After:**
```python
transcript_file = get_output_path("output/transcriptions/transcript.json")
with open(transcript_file, "r") as f:
    data = json.load(f)
```

### 3. Files Updated

- ✅ `/transcribe_video/functions.py` - All 8 file operations
- ✅ `/transcribe_video/scripts/generate_tts_audio.py` - All file operations
- ✅ `/transcribe_video/scripts/demo.py` - All file operations
- ✅ `/transcribe_video/scripts/remove_audio.py` - Already uses argument paths (no changes needed)

## Benefits

1. **Works from any directory**: You can run `python transcribe_video/transcribe.py` from the project root
2. **Consistent paths**: All output files go to the same location regardless of CWD
3. **No more FileNotFoundError**: Files are always found because paths are absolute
4. **Better organization**: All outputs properly organized in the `output/` directory structure

## Directory Structure

```
transcribe_video/
├── functions.py              # Core functions with absolute paths
├── transcribe.py             # Main entry point
├── scripts/
│   ├── generate_tts_audio.py # TTS generation with absolute paths
│   ├── demo.py               # Demo script with absolute paths
│   └── remove_audio.py       # Audio removal (uses arg paths)
└── output/                   # All generated files (auto-created)
    ├── transcriptions/       # Transcript data
    │   ├── transcription.txt
    │   ├── recap_data.json
    │   └── recap_text.txt
    ├── videos/               # Video files
    │   ├── recap_video.mp4
    │   └── recap_video_with_narration.mp4
    └── audio/                # Audio files
        └── recap_narration_timed.mp3
```

## Testing

Run the transcription workflow from any directory:

```bash
# From project root
python transcribe_video/transcribe.py

# Or from transcribe_video directory
cd transcribe_video
python transcribe.py

# Both work correctly now!
```

## Technical Details

- Uses `os.path.abspath(__file__)` to get the absolute path of the script file
- Uses `os.path.dirname()` to get the directory containing the script
- Uses `os.path.join()` to safely combine paths across platforms (Windows/Mac/Linux)
- Creates output directories automatically with `os.makedirs(output_dir, exist_ok=True)`

