# Upload → recap video: workflow and logic

This document describes how **Video Recap Agent** turns an uploaded file into a downloadable **recap video with narration**, as implemented in the backend (`RecapPipeline` in `backend/app/workers/pipeline.py`) and the job/upload APIs.

## 1. High-level flow

1. **Upload**  
   The client uploads the video to object storage (e.g. MinIO/S3). The upload API stores the file under a user-scoped key (e.g. `uploads/{user_id}/...`) and returns metadata including `s3_key`.

2. **Create job**  
   The client calls `POST /api/v1/jobs` with the `s3_key`, filename, size, and **job config** (target duration, Whisper model, TTS voice, optional language / translation, etc.).  
   The API checks quota, optional per-user OpenAI key rules, and that the object exists in storage, then creates a **job** row with `input_video_key` set to that `s3_key` and enqueues **Celery** task `process_recap_job`.

3. **Worker runs the pipeline**  
   A Celery worker loads the job, marks it **processing**, and runs `RecapPipeline.run()`. It uses a **temporary working directory** on the worker machine for all local files.

4. **Progress**  
   Step and percentage updates go to the database and to **Redis pub/sub**; the API WebSocket forwards them so the UI can show live progress.

5. **Completion**  
   The final MP4 is uploaded to storage under `results/{job_id}/recap_video_with_narration.mp4`. The job is marked **completed**, `output_video_key` and `expires_at` are set (e.g. 7 days ahead).  
   If `DELETE_INPUT_VIDEO_ON_COMPLETE` is enabled, the **original upload** is deleted from storage and `input_video_key` is cleared in the DB (output and intermediates remain until expiry or user delete).

6. **Download**  
   The user downloads via `GET /api/v1/jobs/{id}/download`, which streams `output_video_key`.

## 2. Pipeline steps (logic)

Processing is **seven numbered steps** (plus step 0 for “downloading”). Intermediates are **uploaded to object storage** under `jobs/{job_id}/...` so a **stopped/failed** job can **resume** without redoing every step.

| Step | Name (user-facing) | What happens |
|------|---------------------|--------------|
| **0** | Downloading video | The worker **downloads** the file from `input_video_key` into the temp working dir. Without this file, the pipeline cannot run (and resume requires the original until the job completes and input is deleted). |
| **1** | Transcribe | **Whisper** (configurable model size, optional `language`) turns speech in the video into a **structured JSON transcript** (`transcription.json` — array of `{start, end, text}`). A human-readable `.txt` is also written for logging but is not used downstream. Intermediate: `transcription`. |
| **2** | Translate (optional) | If `translate_to` is set, each segment's text is **translated** while preserving the `{start, end, text}` JSON structure; otherwise this step is skipped. Intermediate: `translation` when used. |
| **3** | Generate recap | Two **separate LLM calls** against the JSON transcript: **(a) Clip selection** — selects the most important time windows to fill `target_duration`, returned as `clip_timings` JSON; **(b) Narration** — given the selected clips and full transcript context, writes `recap_text` calibrated to the visual timeline. A `validate_clip_timings` pass sanitizes the LLM output (drops zero-length clips, clamps to video duration, resolves overlaps) before anything touches MoviePy. Intermediate: `recap_data`. |
| **4** | Narration (TTS) | **OpenAI TTS** turns the recap script into **spoken audio** (`tts_model`, `tts_voice`), tuned toward `target_duration`. Intermediate: `tts_audio`. |
| **5** | Extract clips | Using the **original local video** and **recap JSON**, the pipeline **validates clip timings** against the actual video duration (clamping, deduplicating, removing overlaps), then **cuts and assembles** a video montage. A **duration cap** keeps the montage close to the user's target (TTS length + small overshoot). Intermediate: `recap_video`. |
| **6** | Remove audio | **Original audio** is stripped from the montage so the final mix is clean for new narration. Output: video without audio. |
| **7** | Merge | The **narration audio** is **muxed** onto the silent montage with a **max duration** aligned to the same cap as above. Result: one final MP4 with picture + new voiceover. |

Then that file is **uploaded** as the single **user-facing** result; the job row stores `output_video_key`.

## 3. Configuration knobs (job `config`)

- **`target_duration`** — Desired recap length (seconds); drives recap word budget, clip budget, and merge caps.  
- **`whisper_model`** — Whisper size for transcription.  
- **`language` / `translate_to`** — ASR language and optional translation before recap.  
- **`tts_model` / `tts_voice`** — TTS API and voice.  
- **`pad_with_black`** — Handled in video processing where applicable for padding policy.

OpenAI calls (transcription service, translation, recap generation, TTS) use the app’s key and/or a **user-supplied key** depending on feature flags and user settings.

## 4. Resume, stop, and failure

- **Stop** — Running Celery task is revoked; job becomes **stopped**; intermediates already in DB/S3 remain.  
- **Resume** — `POST /jobs/{id}/resume` re-queues the task with `resume_from_step = current_step`. The worker **re-downloads** the original (if `input_video_key` still exists) and **re-downloads intermediates** from S3 from the appropriate step onward. If the original was already removed after a **completed** run, resume is not possible for that job.  
- **Failure** — Exceptions mark the job **failed** and store `error_message`; partial `intermediate_keys` may allow resume from the last completed step.

## 5. Storage and lifecycle

| Artifact | Typical location | Lifecycle |
|----------|------------------|-----------|
| Original upload | `uploads/...` (input key) | Kept until job completes (then optionally deleted) or until whole job is deleted / expired. |
| Intermediates | `jobs/{job_id}/...` | Updated as steps complete; kept on the job row for resume. |
| Final recap | `results/{job_id}/recap_video_with_narration.mp4` | Kept until **expiry** cleanup or **delete job**. |
| DB job row | `recap_jobs` | Tracks status, keys, `expires_at`, etc. |

Periodic **cleanup** (`cleanup_expired_files`) can mark expired jobs and delete output (and any remaining input/intermediates) according to server configuration.

## 6. End-to-end diagram (conceptual)

```mermaid
flowchart LR
  upload[Client upload to S3]
  createJob[POST jobs]
  celery[Celery worker]
  dl[Download input]
  t1[Transcribe JSON]
  t2[Translate optional]
  t3a[LLM: Select clips]
  t3b[LLM: Write narration]
  t4[TTS]
  t5[Validate + Extract clips]
  t6[Strip audio]
  t7[Merge AV]
  out[Upload final MP4]
  upload-->createJob-->celery-->dl
  dl-->t1-->t2-->t3a-->t3b-->t4-->t5-->t6-->t7-->out
```

## 7. Summary

**Uploaded video → recap video** means: store the file → create a job → worker **transcribes to structured JSON** (and optionally **translates**) → **LLM selects clips** → **LLM writes narration for those clips** → **TTS** → **validate + cut video** → **replace audio with narration** → upload **one final MP4** and optionally **drop the original** to save space while keeping the recap until expiry or user deletion.
