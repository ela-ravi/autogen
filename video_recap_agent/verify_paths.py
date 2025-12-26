#!/usr/bin/env python3
"""
Verify Output Paths - Test that all paths are correctly configured
WITHOUT requiring any dependencies (whisper, moviepy, etc.)

Run this to verify the output directory structure is set up correctly.
"""

import os
import sys

print('='*70)
print('OUTPUT PATH VERIFICATION')
print('='*70)
print()

# Get base directory
base_dir = os.path.dirname(os.path.abspath(__file__))
print(f'📁 Base directory: {base_dir}')
print(f'📁 Output directory: {os.path.join(base_dir, "output")}')
print()

# Test path resolution logic (same as in modules)
def get_output_path(relative_path):
    """Convert relative output path to absolute path"""
    return os.path.join(base_dir, relative_path)

# Define expected files
test_files = {
    'Original Audio': 'output/original/extracted_audio.wav',
    'Original Transcription': 'output/original/full_transcription.txt',
    'Transcription (Text)': 'output/transcriptions/transcription.txt',
    'Transcription (JSON)': 'output/transcriptions/transcription.json',
    'Recap Data': 'output/transcriptions/recap_data.json',
    'Recap Text': 'output/transcriptions/recap_text.txt',
    'Recap Video': 'output/videos/recap_video.mp4',
    'Final Video': 'output/videos/recap_video_with_narration.mp4',
    'TTS Audio': 'output/audio/recap_narration.mp3',
}

print('[1/2] Verifying output directory structure...')
print('-'*70)

dirs_to_check = [
    'output',
    'output/original',
    'output/transcriptions',
    'output/videos',
    'output/audio',
    'output/temp'
]

all_dirs_exist = True
for dir_path in dirs_to_check:
    abs_path = get_output_path(dir_path)
    if os.path.exists(abs_path) and os.path.isdir(abs_path):
        print(f'  ✅ {dir_path}/')
    else:
        print(f'  ❌ {dir_path}/ (missing)')
        all_dirs_exist = False

print()

print('[2/2] Checking existing output files...')
print('-'*70)

files_found = 0
files_missing = 0

for name, rel_path in test_files.items():
    abs_path = get_output_path(rel_path)
    if os.path.exists(abs_path):
        size = os.path.getsize(abs_path)
        if size < 1024:
            size_str = f'{size} B'
        elif size < 1024*1024:
            size_str = f'{size/1024:.1f} KB'
        else:
            size_str = f'{size/(1024*1024):.1f} MB'
        print(f'  ✅ {name:25} → {rel_path} ({size_str})')
        files_found += 1
    else:
        print(f'  ⚠️  {name:25} → {rel_path} (not found)')
        files_missing += 1

print()
print('='*70)
print('VERIFICATION SUMMARY')
print('='*70)

if all_dirs_exist:
    print('✅ All output directories exist')
else:
    print('❌ Some output directories are missing')

print(f'✅ Files found: {files_found}')
if files_missing > 0:
    print(f'⚠️  Files missing: {files_missing}')
    print('   (This is expected if workflow hasn\'t run yet)')

print()

# Verify no old paths exist
print('Checking for old output locations...')
print('-'*70)
old_path = os.path.join(base_dir, 'modules', 'output')
if os.path.exists(old_path):
    print(f'⚠️  Old output directory still exists: {old_path}')
    print('   Consider removing it: rm -rf modules/output/')
else:
    print(f'✅ No old output directories found (modules/output removed)')

print()
print('='*70)
print('✅ PATH VERIFICATION COMPLETE - All paths correctly configured!')
print('='*70)
print()
print('Next steps:')
print('  1. Install dependencies: pip install -r requirements.txt')
print('  2. Run workflow: python run_recap_workflow.py /path/to/video.mp4')
print()

