# Root Directory Cleanup Guide

## 🎯 Goal

Clean up the root directory, keeping only what's necessary for a multi-project Autogen repository.

## ✅ What to Keep

```
autogen/
├── .env                    # Environment variables (create if needed)
├── .gitignore             # Git ignore rules
├── README.md              # Main repository README (updated)
└── transcribe_video/      # Self-contained video processing module
```

## ❌ What Can Be Deleted

### Duplicate Files (now in transcribe_video/)
These are all duplicated inside `transcribe_video/`:
- ❌ `run_recap_workflow.py`
- ❌ `test_modular_workflow.py`
- ❌ `QUICK_REFERENCE.md`
- ❌ `docs/` (entire directory)

### Migration/Utility Scripts (no longer needed)
These were used during development and migration:
- ❌ `continue_workflow.py`
- ❌ `post_process_recap.py`
- ❌ `run_complete_workflow.py`
- ❌ `reorganize.py`
- ❌ `update_file_paths.py`
- ❌ `REORGANIZATION_PLAN.md`

## 🔧 Cleanup Options

### Option 1: Automated Cleanup

Run the cleanup script:
```bash
cd /Volumes/Development/Practise/autogen
bash cleanup_root.sh
```

### Option 2: Manual Cleanup

Delete files manually:
```bash
cd /Volumes/Development/Practise/autogen

# Delete duplicate files
rm run_recap_workflow.py
rm test_modular_workflow.py
rm QUICK_REFERENCE.md
rm -rf docs

# Delete utility scripts
rm continue_workflow.py
rm post_process_recap.py
rm run_complete_workflow.py
rm reorganize.py
rm update_file_paths.py
rm REORGANIZATION_PLAN.md

# Optional: delete cleanup script after use
rm cleanup_root.sh
```

### Option 3: Git Clean

If you're using git:
```bash
cd /Volumes/Development/Practise/autogen

# Add transcribe_video to git first
git add transcribe_video/

# Remove old files from git
git rm run_recap_workflow.py
git rm test_modular_workflow.py
git rm QUICK_REFERENCE.md
git rm -r docs/
git rm continue_workflow.py
git rm post_process_recap.py
git rm run_complete_workflow.py
git rm reorganize.py
git rm update_file_paths.py
git rm REORGANIZATION_PLAN.md

# Commit changes
git commit -m "Restructure: Make transcribe_video self-contained"
```

## 📂 Final Structure

After cleanup, your repository should look like:

```
autogen/
├── .env                    # Environment configuration
├── .gitignore             # Git ignore rules  
├── README.md              # Main repo README
│
└── transcribe_video/      # Video processing module
    ├── README.md
    ├── run_recap_workflow.py
    ├── test_modular_workflow.py
    ├── QUICK_REFERENCE.md
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    │
    ├── modules/
    │   ├── __init__.py
    │   ├── transcription.py
    │   ├── video_processing.py
    │   └── audio_processing.py
    │
    ├── scripts/
    │   ├── 01_transcribe.py
    │   ├── 02_translate.py
    │   ├── 03_generate_recap.py
    │   ├── 04_extract_clips.py
    │   ├── 05_remove_audio.py
    │   ├── 06_generate_tts.py
    │   └── 07_merge_audio_video.py
    │
    ├── output/
    │   ├── transcriptions/
    │   ├── videos/
    │   └── audio/
    │
    └── docs/
        ├── MODULAR_WORKFLOW.md
        ├── REFACTORING_COMPLETE.md
        ├── SELF_CONTAINED_MODULE.md
        └── ... (other docs)
```

## ✅ Verification

After cleanup, verify everything works:

```bash
cd transcribe_video
python test_modular_workflow.py
```

Expected output: `✅ All tests passed!`

## 🎉 Benefits After Cleanup

1. **Clean root directory** - Only essential files
2. **Clear structure** - Easy to add more projects
3. **Self-contained modules** - Each project independent
4. **No confusion** - No duplicate files
5. **Ready for growth** - Space for more Autogen projects

## 📝 Notes

- Keep `.env` file if you already have API keys configured
- The new root `README.md` provides overview of all projects
- `transcribe_video/` has everything it needs to work independently
- You can now add other Autogen projects alongside `transcribe_video/`

## 🆘 If Something Breaks

If you accidentally delete something needed:
1. The transcribe_video module is self-contained and should still work
2. All important files are backed up in `transcribe_video/`
3. Run `cd transcribe_video && python test_modular_workflow.py` to verify

## ✨ After Cleanup

Try running the workflow:
```bash
cd transcribe_video
python run_recap_workflow.py /path/to/video.mp4
```

Everything should work perfectly! 🚀

