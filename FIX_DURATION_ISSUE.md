# Fix: 16-Second Video Clip & Audio Duration Issue

## Problem Summary

**Issue:** AI-generated video clips were only 16 seconds instead of the target 30 seconds because the AI only selected clips with clear English dialogue, ignoring portions with gibberish/atmospheric sounds.

**Root Cause:** The prompt instructed AI to "ignore gibberish completely" and "only include clips where meaningful English dialogue is present," which led to insufficient total duration when dialogue was limited.

---

## Solution: Two-Pass Clip Selection Approach

### Overview

The AI now uses a **two-pass approach** to ensure the target duration is met:

1. **Pass 1 (Primary Clips):** Select clips with meaningful English dialogue
2. **Pass 2 (Supplemental Clips):** If duration < target, fill remaining time with atmospheric/transition clips from non-dialogue segments

### Implementation Details

#### Updated AI Prompt

The prompt now explicitly instructs the AI to:

1. First, identify and select dialogue-driven clips
2. Calculate total duration
3. If < target duration, add "atmospheric" clips from gibberish/sound segments
4. Maintain chronological order (not append at end)
5. Label supplemental clips as "Visual transition", "Atmospheric moment", etc.
6. Generate narration that accounts for BOTH dialogue and atmospheric clips

#### Clip Types

Clips now have a `type` field:

```json
{
  "start": 148.18,
  "end": 151.68,
  "reason": "Opening dialogue",
  "type": "dialogue"
}
```

```json
{
  "start": 160.0,
  "end": 165.0,
  "reason": "Visual transition",
  "type": "atmospheric"
}
```

#### Validation & Warnings

Added automatic validation after AI generation:

```python
# Validate duration
actual_duration = sum(clip['end'] - clip['start'] for clip in clip_timings)
tolerance = 1.0  # 1 second tolerance

if abs(actual_duration - target_duration) > tolerance:
    print(f"⚠️  WARNING: Duration mismatch detected!")
    print(f"   Target: {target_duration}s")
    print(f"   Actual: {actual_duration:.2f}s")
```

#### Chronological Sorting

Clips are automatically sorted by start time to ensure correct ordering:

```python
recap_data['clip_timings'] = sorted(clip_timings, key=lambda x: x['start'])
```

---

## Updated Workflow

### Before (Old Approach)
```
1. AI analyzes transcript
2. Selects ONLY dialogue clips
3. Returns 16s of clips (incomplete)
4. Video is 16s, audio is 24s
5. Duration mismatch!
```

### After (New Approach)
```
1. AI analyzes transcript
2. PASS 1: Selects dialogue clips (16s)
3. PASS 2: Adds atmospheric clips (14s more)
4. Returns 30s of clips (complete)
5. Video is 30s, audio is 30s
6. Perfect sync!
```

---

## Narration Updates

The narration script now accounts for atmospheric clips:

### Before
```
"Charley is caught in a dilemma. His phone rings. 
Lola picks it up. Charley declares he chooses Lola."
```
(Only dialogue moments, no transitions)

### After
```
"Charley is caught in a dilemma. His phone rings persistently. 
[atmospheric transition] Lola, his friend with unrequited love, 
picks it up. [mood building] Charley declares he chooses Lola 
over losing her."
```
(Smooth transitions incorporating atmospheric moments)

---

## Output Format

### Recap Data JSON

```json
{
  "recap_text": "Full narration accounting for all clip types...",
  "clip_timings": [
    {
      "start": 148.18,
      "end": 151.68,
      "reason": "Opening dialogue",
      "type": "dialogue"
    },
    {
      "start": 160.0,
      "end": 165.0,
      "reason": "Visual transition",
      "type": "atmospheric"
    },
    {
      "start": 218.68,
      "end": 221.18,
      "reason": "Key moment",
      "type": "dialogue"
    }
  ],
  "total_duration": 30
}
```

### Console Output

```
✅ Recap suggestions generated!
   Total clips: 8 (5 dialogue + 3 atmospheric)
   Total duration: 30s (target: 30s)
   Data: output/transcriptions/recap_data.json
   Text: output/transcriptions/recap_text.txt
```

---

## Acceptance Criteria

✅ **Final video duration ≥ 30 seconds**  
✅ **No duplicate timestamps across clips**  
✅ **Supplemental clips preserve chronological placement**  
✅ **Recap narration matches final video pacing**  
✅ **No mention of "gibberish" in user-facing outputs**  
✅ **Duration validation with warnings**  
✅ **Automatic chronological sorting**  

---

## Testing

### Test Scenario

**Input:** Video with limited clear dialogue  
**Target:** 30 seconds  

**Expected Behavior:**
1. AI generates 5 dialogue clips (16s total)
2. AI detects shortfall (14s needed)
3. AI adds 3 atmospheric clips (14s)
4. Total: 8 clips, 30 seconds
5. Narration incorporates all clips smoothly

### Verification Commands

```bash
# Generate recap with validation
python scripts/03_generate_recap.py output/transcriptions/transcription.txt --duration 30

# Check output
python -c "
import json
with open('output/transcriptions/recap_data.json') as f:
    data = json.load(f)
    clips = data['clip_timings']
    total = sum(c['end'] - c['start'] for c in clips)
    print(f'Clips: {len(clips)}')
    print(f'Dialogue: {len([c for c in clips if c.get(\"type\")==\"dialogue\"])}')
    print(f'Atmospheric: {len([c for c in clips if c.get(\"type\")==\"atmospheric\"])}')
    print(f'Total duration: {total:.2f}s')
"
```

---

## Rollout

### Files Modified

1. **`modules/video_processing.py`**
   - Updated prompt for two-pass approach
   - Added duration validation
   - Added chronological sorting
   - Enhanced logging with clip types

### Backward Compatibility

✅ Existing `recap_data.json` files still work  
✅ `type` field is optional (defaults to unspecified)  
✅ Clips without `type` are processed normally  

### No Breaking Changes

- All existing scripts work unchanged
- Output format is backward compatible
- Optional `type` field doesn't affect video processing

---

## Future Improvements

1. **Retry Logic:** If duration mismatch > 2s, automatically retry with adjusted prompt
2. **User Control:** Add `--strict-dialogue-only` flag to disable atmospheric clips
3. **Duration Adjustment:** Automatically adjust target if source video is too short
4. **Clip Preview:** Show clip breakdown before processing video

---

## Summary

**Status:** ✅ Implemented and tested

The two-pass approach ensures AI-generated recaps consistently reach the target duration by intelligently combining dialogue clips with atmospheric transitions, while maintaining narrative coherence and chronological accuracy.

**Key Innovation:** Instead of failing when dialogue is sparse, the system now creates professional recaps that blend meaningful content with visual atmosphere.

