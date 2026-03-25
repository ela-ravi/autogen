#!/usr/bin/env python3
"""
Resume Workflow: From Audio Extraction

Use this when you have the original video but want to skip nothing.
This is essentially the same as the full workflow but makes it clear
you're starting from the beginning.

Usage:
    python resume/from_audio_extraction.py /path/to/video.mp4 [options]
    
Example:
    python resume/from_audio_extraction.py /path/to/video.mp4 --duration 30
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import and run the main workflow
from run_recap_workflow import main

if __name__ == "__main__":
    print("\n" + "="*80)
    print("RESUMING FROM: Audio Extraction (Full Workflow)")
    print("="*80)
    print("This will run the complete workflow from the beginning.\n")
    main()

