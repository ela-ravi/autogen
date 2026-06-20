# Codebase Q&A: Video Recap Pipeline

Comprehensive Q&A documenting pipeline mechanics, edge cases, and improvement areas.

---

## Q1: How are timestamps handled from LLM to FFMPEG?

### Answer
GPT-4 returns clip timings as JSON with float timestamps in seconds:
```json
{
  "clip_timings": [
    {"start": 0.5, "end": 10.2, "reason": "key moment"},
    {"start": 15.0, "end": 25.5, "reason": "dialogue"}
  ]
}
```

moviepy's `subclip(start, end)` then cuts the video using these exact timestamps. The `validate_clip_timings()` function sanitizes the timings before cutting:
- Negative/zero-length clips are dropped
- Overlapping ranges are resolved (later clip trimmed)
- Out-of-bounds clips are clamped to video duration
- Non-chronological clips are sorted

### File Location
- `modules/video_processing.py:55` - `validate_clip_timings()`
- `modules/video_processing.py:329-356` - Clip extraction loop

### Improvements Needed
1. **Timestamp Precision**: Currently rounds to 1-2 decimals. Consider:
   - Allow user-configurable precision for frame-accurate cutting
   - Document rounding behavior in API response
   - Add validation that start < end before processing

2. **Overlap Resolution**: Currently trims later clip. Consider:
   - Add option to merge overlapping clips instead of trimming
   - Log which clips were trimmed and why
   - Alert user if significant content was lost to trimming

3. **Boundary Clipping**: Silently clamps to video_duration. Consider:
   - Log warnings when clips are clamped
   - Add metric: "X% of requested clips fell outside video bounds"
   - Option to fail if any clip is out-of-bounds

---

## Q2: How is target duration enforced? Can LLM achieve exact length?

### Answer
**Three-tier approach with fallback**:

**Tier 1 - Smart LLM Selection** (3 retry loop):
1. LLM selects clips targeting exactly `target_duration` ± 2 seconds
2. If duration misses tolerance, LLM is shown the error and asked to adjust
3. Retries up to 3 times
4. If still off: proceed to Tier 2

**Tier 2 - Proportional Scaling**:
If after 3 attempts duration is still wrong, scale all clips proportionally:
```python
scale = target_duration / actual_duration
for clip in clip_timings:
    mid = (clip["start"] + clip["end"]) / 2
    half = ((clip["end"] - clip["start"]) * scale) / 2
    clip["start"] = max(0, round(mid - half, 1))
    clip["end"] = round(mid + half, 1)
```

**Tier 3 - Hard Trim**:
Final video is trimmed to exactly `target_duration` using `subclip(0, target_duration)`

### File Location
- `modules/video_processing.py:89-283` - `generate_recap_suggestions()` with retry logic
- `modules/video_processing.py:354-356` - Final trim

### Improvements Needed
1. **Duration Predictability**: Currently relies on LLM's ability to estimate. Consider:
   - Pre-calculate word count → estimated TTS duration (use empirical model)
   - Reduce clip count if estimated duration too long
   - Add metadata: "estimated_duration", "actual_duration", "adjustment_factor"

2. **Scaling Quality**: Proportional scaling maintains aspect ratio but may distort content. Consider:
   - Add option to add/remove clips instead of scaling
   - Let LLM know scaling will happen: "If you select X duration, it will be scaled to Y"
   - Preserve original clip reasons in scaled output

3. **Hard Trim Loss**: Final trim can abruptly cut content. Consider:
   - Add fade-out to final clip if trimmed
   - Log which clip(s) were trimmed by final trim
   - Option to prefer removing clips over trimming last clip

4. **Tolerance Documentation**: ±2s tolerance is hardcoded. Consider:
   - Make configurable via job config
   - Expose in API: show user actual vs requested duration
   - Warning if tolerance exceeded before trim

---

## Q3: Are there quality checks for edge cases?

### Answer
**Status: MINIMAL**

**Handled**:
✅ Overlapping clips (trims later clip)
✅ Non-chronological order (sorts)
✅ Out-of-bounds timings (clamps)
✅ Zero/negative-length clips (drops)
✅ Audio duration mismatch (pads or trims)

**Not Handled**:
❌ Very short videos (< target_duration)
❌ Insufficient meaningful content (all clips are silence)
❌ Transcription quality (garbled/low-confidence segments)
❌ Invalid JSON from LLM (basic markdown stripping only)
❌ LLM timeouts or rate limit errors
❌ Video codec compatibility issues

### File Location
- `modules/video_processing.py:55-86` - `validate_clip_timings()` - only handles timing issues

### Improvements Needed
1. **Transcription Quality Check**:
   ```python
   # Add to Step 1:
   - Check confidence scores from Whisper per segment
   - Flag low-confidence segments (< 0.5 confidence)
   - Alert user if > 30% of video is low-confidence
   - Option: skip low-confidence segments from recap consideration
   ```

2. **Content Sufficiency Check**:
   ```python
   # Add to Step 3:
   - Count non-silence segments in transcript
   - If total non-silence < 1.5 * target_duration, warn user
   - Suggest increasing target_duration or using silence-padding mode
   - Block processing if < 0.5 * target_duration available
   ```

3. **Video Compatibility Check**:
   ```python
   # Add to Step 0 (before pipeline):
   - Probe video with ffprobe to check format, codec, duration
   - Validate bitrate, resolution, frame rate
   - Warn if unusual format (8K, 1fps, etc.)
   - Log all metadata for debugging
   ```

4. **LLM Robustness**:
   ```python
   # Improve in Step 3:
   - Try up to 5 times on parse failures (not just duration)
   - Fall back to simpler prompt if complex prompt fails
   - Validate returned JSON schema before using
   - Add human review option for edge cases
   ```

5. **Error Recovery**:
   ```python
   # Add to job model:
   - max_retry_count field (configurable per user)
   - Exponential backoff for API retries
   - Option to skip problematic steps (e.g., translation, TTS)
   - Resume suggests: "Step X failed; try Step Y next"
   ```

---

## Q4: How is audio removed? Is silence detection used?

### Answer
**Method: Complete Audio Stripping**

No silence detection. Uses moviepy's built-in method:
```python
video_no_audio = video.without_audio()
video_no_audio.write_videofile(output_video, codec="libx264", audio=False)
```

This completely removes the audio track without any attempt to detect, preserve, or pad silence. The video container is re-encoded without an audio stream.

### File Location
- `modules/video_processing.py:400-449` - `remove_audio_from_video()`

### Improvements Needed
1. **Option to Preserve Silence**:
   ```python
   # Add parameter: preserve_silent_segments
   - If True: detect silence segments and replace with padding
   - Use librosa or pydub to detect silence (< -40dB for > 0.5s)
   - Preserve timestamp alignment for subtitles
   - Use case: videos with intentional dramatic pauses
   ```

2. **Audio Track Analysis**:
   ```python
   # Add metadata extraction:
   - Silence duration in original
   - Audio levels (peak, RMS)
   - Speech vs music segments
   - Use for: deciding if audio removal is appropriate
   ```

3. **Fade-Out Options**:
   ```python
   # Add parameter: fade_out_duration
   - Apply fade-out to video before silence
   - Smooths transition to narration
   - Use case: professional-looking transitions
   ```

4. **Optional Audio Replacement**:
   ```python
   # Current: removes audio, then adds TTS
   # Improve: Option to blend original audio at low volume
   - Original audio at 10-20% volume + TTS at 100%
   - Use case: maintain ambient sound (background noise, music)
   - Add parameter: keep_original_audio_level (0-100%)
   ```

---

## Q5: How does duration-based clip selection work?

### Answer
**Target Duration**: User specifies desired recap length (default: 30s)

**Narration Word Target**: Calculated from duration:
```python
narration_word_target = max(35, min(220, round(target_duration * 2.0)))
# 30s → ~60 words
# Range: 25-230 words
```

**LLM Approach**:
1. **Call 1 (Clip Selection)**: "Select clips that total exactly {target_duration}s"
2. **Call 2 (Narration)**: "Write {narration_word_target} words to narrate these clips"

**Duration Matching**:
- Clips are summed: `actual_duration = sum(end - start for each clip)`
- Must match target within ±2 seconds
- If not: retry or scale

### File Location
- `modules/video_processing.py:125-128` - Word target calculation
- `modules/video_processing.py:144-161` - Clip selection prompt
- `modules/video_processing.py:163-207` - Duration matching loop

### Improvements Needed
1. **TTS Duration Prediction**:
   ```python
   # Current: Don't know audio length until TTS is generated
   # Improve: Predict TTS duration from word count
   - Empirical model: word_count / average_speech_rate
   - Average: 120-150 words per minute (2-2.5 words/sec)
   - Build from historical data: track actual vs predicted
   - Adjust narration length if prediction misses
   ```

2. **Visual Vs Audio Pacing**:
   ```python
   # Current: Clip duration and narration duration may not match
   # Improve: Sync them in clip selection
   - For each clip, estimate narration for that moment
   - Ensure narration fits within clip duration
   - Add metadata: "this clip needs ~2 seconds of narration"
   - LLM uses both clip duration AND narration duration constraints
   ```

3. **Graceful Undershooting**:
   ```python
   # Current: If insufficient content, hard trim or padding
   # Improve: Signal to LLM early
   - Pre-check: if total available content < 1.5 * target, warn
   - Option 1: Reduce target_duration
   - Option 2: Add padding/transitions
   - Option 3: Fail fast instead of creating low-quality recap
   ```

4. **Multi-Duration Options**:
   ```python
   # Current: Single target_duration
   # Improve: Generate multiple durations in one pass
   - "Generate recaps for 15s, 30s, and 60s"
   - Reuse same LLM call with 3 variants
   - User picks best one
   - Save API cost on re-runs
   ```

---

## Q6: What happens if LLM response fails to parse?

### Answer
**Minimal Error Handling**

Current implementation in `_parse_llm_json()`:
```python
def _parse_llm_json(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())
```

This:
1. Strips markdown fence ` ``` `
2. Removes "json" keyword
3. Calls `json.loads()` - fails if invalid JSON

**No fallback or retry on parse error.**

### File Location
- `modules/video_processing.py:22-29` - `_parse_llm_json()`

### Improvements Needed
1. **Robust JSON Extraction**:
   ```python
   def _parse_llm_json_robust(raw: str, max_retries=3) -> dict:
       # Try 1: Direct parse
       try:
           return json.loads(raw)
       except:
           pass
       
       # Try 2: Remove markdown
       text = re.sub(r'^```json\n?', '', raw)
       text = re.sub(r'\n?```$', '', text)
       try:
           return json.loads(text)
       except:
           pass
       
       # Try 3: Extract JSON object with regex
       match = re.search(r'\{.*\}', raw, re.DOTALL)
       if match:
           try:
               return json.loads(match.group())
           except:
               pass
       
       # Try 4: Retry with LLM
       if max_retries > 0:
           # Ask LLM to fix format
           pass
       
       # Try 5: Return fallback
       return {}
   ```

2. **Validation After Parse**:
   ```python
   # After parsing, validate schema:
   - Check required fields exist (clip_timings, recap_text)
   - Check data types (start/end are float, text is string)
   - Check clip_timings is non-empty list
   - Log validation errors clearly
   ```

3. **User-Facing Error Messages**:
   ```python
   # Current: Silent failures or generic errors
   # Improve:
   - "LLM response was invalid JSON. Retrying..."
   - "Step 3 failed 3 times. Try with simpler prompt?"
   - Show user the raw LLM response for debugging
   - Allow manual clip selection fallback
   ```

4. **Rate Limiting & Backoff**:
   ```python
   # Add retry strategy:
   - Exponential backoff: 1s, 2s, 4s, 8s
   - Max retries: 5
   - Different backoff for rate limit (429) vs other errors
   - Log all retries with timestamps
   ```

---

## Q7: How is checkpoint resumption implemented?

### Answer
**S3-Based Intermediate Storage**

Each step uploads artifacts to S3 in the pattern: `jobs/{job_id}/{step_name}/{filename}`

Intermediates dict example:
```json
{
  "transcription": "jobs/job-123/transcription/transcription.json",
  "translation": "jobs/job-123/translation/tamil_transcription.json",
  "recap_data": "jobs/job-123/recap_data/recap_data.json",
  "tts_audio": "jobs/job-123/tts_audio/recap_narration.mp3",
  "recap_video": "jobs/job-123/recap_video/recap_video.mp4"
}
```

On resumption:
1. User provides `resume_from_step` (0-7)
2. Pipeline downloads relevant intermediates from S3
3. Skips completed steps
4. Runs remaining steps

### File Location
- `backend/app/workers/pipeline.py:53-70` - `_upload_intermediate()`, `_download_intermediate()`
- `backend/app/workers/pipeline.py:106-147` - Resumption logic

### Improvements Needed
1. **Resumption UI**:
   ```python
   # Current: Backend supports resumption, frontend may not expose it
   # Improve:
   - Show user which steps completed in job details
   - "Resume from Step X" dropdown
   - Cost estimate: "Skip steps 1-3, save ~$0.15"
   - One-click resume button
   ```

2. **Intermediate Cleanup**:
   ```python
   # Current: Intermediates kept forever in S3
   # Improve:
   - Auto-delete after job completion (configurable)
   - Option: keep for 7 days for resumption
   - User manual delete option
   - Track storage cost: "Using 500MB for resumption"
   ```

3. **Partial Resumption**:
   ```python
   # Current: Can't change config and resume
   # Improve:
   - Allow changing target_duration on resume from step 3
   - Allow changing voice/TTS model on resume from step 6
   - Re-run only affected downstream steps
   - Show what changed: "Duration changed 30s→60s, re-running steps 3-7"
   ```

4. **Resumption Reliability**:
   ```python
   # Add safeguards:
   - Checksum verification of downloaded intermediates
   - Timestamp validation: ensure intermediates are from same job_id
   - Handle case where S3 file was deleted externally
   - Option to force restart if intermediates corrupted
   ```

5. **Cost Tracking**:
   ```python
   # Add to job model:
   - cost_by_step: {"transcription": 0, "recap": 0.15, "tts": 0.02}
   - total_cost_saved_by_resumption: $0.15
   - cumulative_cost: $0.42 (across all attempts)
   - Expose in UI for user awareness
   ```

---

## Q8: How does the LLM choose which clips to select?

### Answer
**Two Criteria (Implicit in Prompt)**:

1. **Importance**: "Pick segments with the most important or interesting content first"
2. **Coverage**: "Think about coverage, pacing, and avoiding redundancy"

LLM receives:
- Full transcript as JSON with timestamps
- Target duration
- Rules (no overlaps, no duplicates, chronological order)

LLM returns:
- Clip timings with `reason` field (e.g., "key moment", "dialogue", "transition")

**Reasons are descriptive but not scored.**

### File Location
- `modules/video_processing.py:133-161` - Clip selection system prompt and user prompt

### Improvements Needed
1. **Explicit Scoring System** (for audio-emotions feature):
   ```python
   # Proposed enhancement:
   # Instead of implicit importance, score each segment:
   score_segment = {
       "start": 0.5,
       "end": 2.3,
       "text": "...",
       "importance": 0.8,  # 0-1: How critical to understanding
       "emotion": 0.9,     # 0-1: Emotional intensity (new)
       "interest": 0.7,    # 0-1: Engagement level
       "novelty": 0.6      # 0-1: How unique vs. rest of video
   }
   
   # LLM weights them:
   # final_score = 0.4 * importance + 0.3 * emotion + 0.2 * interest + 0.1 * novelty
   # Select top clips by final_score
   ```

2. **Emotion Detection** (audio-emotions feature):
   ```python
   # Add emotion analysis to Step 1:
   - Analyze transcript for emotional keywords
   - Detect tone shifts (excitement, surprise, sadness)
   - Use Azure Text Analytics or similar
   - Store emotion scores per segment
   
   # Modify Step 3:
   - Include emotion scores in clip selection prompt
   - "Prioritize moments with high emotional intensity"
   - Weight emotion as secondary factor after importance
   ```

3. **Diversity Scoring**:
   ```python
   # Current: No scoring for diversity/redundancy
   # Improve:
   - Track topic/keyword usage across selected clips
   - If clip talks about same topic as previous, reduce score
   - Penalize back-to-back clips from same speaker
   - Result: More varied, less repetitive recaps
   ```

4. **Reason Extraction**:
   ```python
   # Current: Reasons in JSON but not used
   # Improve:
   - Parse reason field to extract reason_type: "dialogue", "transition", "climax"
   - Store reason_type in database
   - Use to understand why clips were selected
   - Analytics: "Most selected reason: dialogue (40%)"
   ```

5. **Visual Scoring**:
   ```python
   # Current: Only audio/transcript considered
   # Improve: (requires computer vision)
   - Scene changes, cuts, camera movement
   - Text on screen (subtitles, captions)
   - Visual complexity (busy vs. static scenes)
   - Add as additional clip scoring factor
   ```

---

## Q9: What's the cost breakdown per video?

### Answer
**Approximate Costs (OpenAI 2024 Pricing)**:

| Step | Cost | Notes |
|------|------|-------|
| 1. Transcription | FREE | Whisper runs locally |
| 2. Translation | ~$0.02-0.05 | GPT-4o, ~100 tokens per segment |
| 3. Recap Generation | ~$0.10-0.30 | 2 GPT-4o calls: clip selection + narration |
| 4. Clip Extraction | FREE | Local moviepy processing |
| 5. Remove Audio | FREE | Local moviepy processing |
| 6. TTS | ~$0.015-0.025 | TTS price: $0.015 per 1K chars |
| 7. Merge | FREE | Local moviepy processing |
| **Total** | **~$0.12-0.40** | Per 10-minute video |

### File Location
- `README.md:143-151` - Documented cost estimate
- `backend/app/services/billing_service.py` - Actual cost tracking

### Improvements Needed
1. **Cost Prediction**:
   ```python
   # Before processing, estimate cost:
   def estimate_cost(video_duration, config):
       transcript_tokens = video_duration * 0.1  # estimate
       translation_cost = 0.0005 * transcript_tokens if config.translate else 0
       recap_cost = 0.0015 * transcript_tokens  # 2 calls
       tts_chars = config.target_duration * 4  # ~4 chars/word, ~2 words/sec
       tts_cost = 0.000015 * tts_chars
       total = translation_cost + recap_cost + tts_cost
       return total
   # Show to user: "This will cost ~$0.25. Continue?"
   ```

2. **Per-Step Cost Tracking**:
   ```python
   # Add to job model:
   - cost_by_step dict: step name → actual cost
   - Update after each step
   - Show in job details: "Transcription: $0.00, Recap: $0.23, TTS: $0.02"
   - User can optimize: "Use GPT-3.5 to save $0.15"
   ```

3. **Cost Optimization Options**:
   ```python
   # In JobConfig, add:
   - use_cheap_model: bool (gpt-3.5 instead of gpt-4o, saves 80%)
   - skip_translation: bool (saves $0.02-0.05)
   - use_tts_1: bool (instead of tts-1-hd, same cost but faster)
   - target_duration: explicit cost per second
   
   # Show cost tradeoffs in UI
   ```

4. **Cumulative Cost Dashboard**:
   ```python
   # Add to user account:
   - Total cost this month: $12.50
   - Cost per video: $0.23 (average)
   - Most expensive step: Recap generation (58%)
   - Projection: $185/month at current rate
   - Budget alerts: "On track to exceed $100/month"
   ```

---

## Q10: What happens with very short videos?

### Answer
**No Special Handling**

For a 5-second video with 30-second target duration:
1. Transcription: ~5-10 words
2. LLM asked to select 30 seconds from 5 seconds of content
3. LLM returns clips that sum to < 5 seconds
4. Scaling algorithm tries to stretch clips
5. Hard trim removes nothing (video < target)
6. Final output: 5-second video with 30-second narration (long silence after)

**Result: Mismatch between video and audio, poor UX**

### File Location
- No validation in any step
- Related: `modules/audio_processing.py:156-172` - Silence padding on merge

### Improvements Needed
1. **Pre-Processing Validation** (Critical):
   ```python
   # Add to step 0:
   def validate_input_video(video_duration, config):
       target = config.target_duration
       if video_duration < target * 0.5:
           raise ValueError(
               f"Video too short ({video_duration}s) for target duration "
               f"({target}s). Min required: {target * 0.5}s"
           )
       if video_duration < target * 0.75:
           return Warning(
               f"Video is shorter than target. Output may have long silences. "
               f"Consider reducing target_duration to {video_duration * 0.7}s"
           )
   ```

2. **Intelligent Target Adjustment**:
   ```python
   # When video is short, auto-adjust:
   def suggest_target_duration(video_duration):
       # Return reasonable defaults
       if video_duration < 15:
           return 10
       if video_duration < 30:
           return 20
       return 30
   
   # Show to user: "Video is 20s. Suggest target 15s instead of 30s. OK?"
   ```

3. **Padding Strategies**:
   ```python
   # If must use long target on short video:
   - Option 1: Extend clips with fade-in/fade-out
   - Option 2: Add intro/outro cards
   - Option 3: Repeat key clips
   - Option 4: Add visual transitions/text overlays
   - Config option: padding_strategy = "fade" | "repeat" | "silence"
   ```

4. **Silence Handling**:
   ```python
   # Current: Pads with silence
   # Improve:
   - Detect if final video would have > 2s continuous silence
   - Warn user: "Final video has 8s of silence at end"
   - Option: trim silent sections automatically
   - Option: add music background track
   ```

5. **User Guidance**:
   ```python
   # In frontend:
   - Show recommended target_duration based on input length
   - Show estimate: "Video length: 25s. Recommended recap: 15-20s"
   - Disable submissions for unrealistic configs
   - Tooltip: "Recap can't be longer than ~90% of video length"
   ```

---

## Q11: How does the backend handle concurrent jobs?

### Answer
**Celery Task Queue**

- Each job spawns a Celery task via `process_recap_job(job_id, resume_from_step)`
- Celery workers process tasks concurrently (default: 4 workers)
- Redis pub/sub publishes progress in real-time
- Database tracks job state

**No explicit queue limiting or priority handling.**

### File Location
- `backend/app/workers/tasks.py:74-176` - Main Celery task
- `backend/app/workers/celery_app.py` - Celery configuration

### Improvements Needed
1. **Queue Management**:
   ```python
   # Add queue limiting:
   - Max jobs per user: 5 concurrent (prevent abuse)
   - Max jobs overall: 20 concurrent (resource constraint)
   - Queue status endpoint: show queue length
   - Queue time estimate: "Your job will start in ~2 minutes"
   ```

2. **Priority Queues**:
   ```python
   # Add priority levels:
   - Default: Normal (FIFO)
   - Premium: Skip queue (if user has paid tier)
   - Batch: Lower priority (good for night jobs)
   - Celery routing: @celery_app.task(queue='high_priority')
   ```

3. **Job Lifecycle Logging**:
   ```python
   # Add to job model:
   - queued_at: when job created
   - started_at: when Celery picked it up
   - queue_duration: started_at - queued_at
   - step_timings: dict of {step: duration_seconds}
   - total_duration: queued_at to completed_at
   
   # Analytics: "Avg queue time: 30s, avg processing time: 120s"
   ```

4. **Resource Limiting**:
   ```python
   # Add controls:
   - Max concurrent jobs per GPU (if using GPU)
   - Memory limit per job: kill if exceeds 1.5GB
   - Timeout per step: cancel if step > 5 minutes
   - Celery timeout: task_soft_time_limit=300, task_time_limit=600
   ```

5. **Monitoring & Alerts**:
   ```python
   # Add observability:
   - Celery tasks registered: show in health check
   - Active tasks: endpoint showing running jobs
   - Failed tasks: automatic retry or alert
   - Celery queue depth: alert if > 10 jobs queued
   - Worker health: alert if worker down
   ```

---

## Q12: What can be improved in the emotion detection feature?

### Answer
**This is the current `audio-emotions` branch goal.**

Current system: Selects clips by importance/coverage only.

Proposed: Weight emotional content in selection.

### Improvements for Implementation
1. **Emotion Analysis Phase** (new Step 2.5):
   ```python
   def analyze_emotions(transcript_segments):
       """Score each segment for emotional intensity."""
       emotions = ["joy", "surprise", "anger", "sadness", "fear", "disgust", "neutral"]
       
       for segment in transcript_segments:
           # Option A: Regex keyword matching (simple, fast)
           # Option B: Azure Text Analytics (robust, paid)
           # Option C: OpenAI sentiment analysis (flexible)
           
           segment["emotions"] = {
               "dominant_emotion": "joy",
               "intensity": 0.85,  # 0-1
               "confidence": 0.92,
               "keywords": ["excited", "amazing", "love"]
           }
       return transcript_segments
   ```

2. **Clip Selection Scoring** (modify Step 3, Call 1):
   ```python
   # Instead of just:
   # "Select the most important moments"
   
   # New prompt:
   # "Select important moments, prioritizing emotional highlights:
   #  - High-emotion segments (joy, surprise, anger) score 2x importance
   #  - Peak emotional moments (intensity > 0.8) are must-include
   #  - Avoid consecutive clips with same emotion (variety)
   #  - Balance emotions: mix joy/surprise with serious moments"
   
   # LLM receives:
   [
     {"start": 0.5, "end": 2.3, "text": "...", "emotion": "joy", "intensity": 0.9},
     {"start": 2.5, "end": 5.1, "text": "...", "emotion": "neutral", "intensity": 0.3},
     ...
   ]
   ```

3. **Weighting Strategy**:
   ```python
   # In LLM prompt, explain weighting:
   score = (
       0.4 * importance_score +        # Still important
       0.4 * emotional_intensity +     # NEW: Emotional weight
       0.1 * diversity_score +         # Avoid repetition
       0.1 * pacing_score              # Visual rhythm
   )
   # Select top N clips by score
   ```

4. **Narration Adjustment**:
   ```python
   # Modify Step 3, Call 2:
   # Current: "Write narration for these clips"
   # New: "Write narration that amplifies emotional peaks"
   
   # Changes:
   - Tone shifts: match narration tone to clip emotion
   - Pacing: pause after emotional moments
   - Emphasis: use stronger language for high-emotion clips
   - Example: For joy clip, use enthusiastic tone; for sadness, slower pacing
   ```

5. **A/B Testing Framework**:
   ```python
   # To validate emotion feature:
   - Generate both versions: with and without emotion weighting
   - Show to user: "Version A" vs "Version B"
   - Collect feedback: "Which is more engaging?" (1-10)
   - Track metrics:
     * User satisfaction score
     * View duration (how far do they watch)
     * Share rate (do they share it)
   - Result: data-driven decision to keep or refine
   ```

6. **Configuration Options**:
   ```python
   # Add to JobConfig:
   - emotion_weighting: 0-1 (0=off, 1=max emotion priority)
   - emotions_to_prefer: list (e.g., ["joy", "surprise"])
   - emotions_to_avoid: list (e.g., ["disgust"])
   - emotion_balance: "diverse" | "consistent" (mix vs. pure emotions)
   - narration_tone: "neutral" | "enthusiastic" | "empathetic"
   ```

7. **Fallback for Undetected Emotion**:
   ```python
   # Edge case: Whisper can't detect emotion (no speech/music)
   # Solution:
   - Default emotion scores to neutral
   - Use visual analysis as backup (if available)
   - Show warning: "Emotion detection confidence low (50%)"
   - Allow manual emotion annotation by user
   ```

---

## Quick Reference: Most Important Files

| File | Purpose | When to Modify |
|------|---------|----------------|
| `modules/transcription.py` | Step 1-2: Transcribe & translate | Whisper model, language handling |
| `modules/video_processing.py` | Step 3-5: AI recap, clip extraction, audio removal | Clip selection logic, duration handling |
| `modules/audio_processing.py` | Step 6-7: TTS, audio merge | Voice options, audio alignment |
| `backend/app/workers/pipeline.py` | Pipeline orchestration | Resumption, S3 integration |
| `backend/app/workers/tasks.py` | Celery task definition | Job status, error handling |
| `backend/app/models/job.py` | Job database schema | Tracking new metrics |
| `frontend/src/components/upload/` | Video upload UI | User-facing config options |

---

## Summary: What's Working Well

✅ **Modular design**: Each step is independent, testable, reusable
✅ **Checkpoint resumption**: S3 storage enables cost-saving resumption
✅ **Flexible duration handling**: 3-tier approach (retry → scale → trim)
✅ **Real-time progress**: Redis pub/sub for live updates
✅ **LLM-driven selection**: Avoids hard-coded rules, adapts to content

---

## Summary: Critical Gaps to Address

❌ **No quality validation**: Very short videos, insufficient content, garbled transcription
❌ **Minimal error handling**: Parse failures, API timeouts, rate limits
❌ **No emotion detection**: Currently only importance-based (audio-emotions goal)
❌ **Silent audio stripping**: No silence preservation, no original audio blending
❌ **No user guidance**: Unrealistic configs accepted without warning
❌ **Limited monitoring**: No per-step cost tracking, no queue management

---

**Last Updated**: 2026-05-15
**Branch**: audio-emotions
**Status**: Understanding complete, ready for implementation

