# Recap Generation Workflow

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INPUT                               │
│  • Video Path                                               │
│  • Source Language                                          │
│  • Target Language                                          │
│  • Create Recap? (yes/no)                                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                AUTOGEN AGENTS                               │
│  ┌──────────────┐         ┌────────────────┐              │
│  │   Chatbot    │◄───────►│  User Proxy    │              │
│  │   (GPT-4)    │         │   (Executor)   │              │
│  └──────────────┘         └────────────────┘              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────────┐
         │   WORKFLOW ORCHESTRATION   │
         └────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
   ┌────────┐   ┌──────────┐   ┌───────────┐
   │ STEP 1 │   │  STEP 2  │   │  STEP 3   │
   └────────┘   └──────────┘   └───────────┘
```

## Detailed Workflow

### Step 1: Video Transcription 🎤
```
Function: recognize_transcript_from_video()

Input:  video_file.mp4
   │
   ├─► Load Whisper Model (small)
   │
   ├─► Transcribe with timestamps
   │
   └─► Output: transcription.txt
       
       Example:
       0s to 5.0s: I can't believe I did this!
       5.0s to 7.0s: I can't believe I did this.
       ...
```

### Step 2: Translation 🌍
```
Function: translate_transcript()

Input:  transcription.txt + target_language
   │
   ├─► Read each timestamped line
   │
   ├─► Call GPT-4 for translation
   │
   └─► Output: {target_language}_transcription.txt
       
       Example (Tamil):
       0s to 5.0s: 'நான் இதை செய்ததாக நான் நம்ப முடியவில்லை!'
       ...
```

### Step 3: AI Recap Generation 🤖
```
Function: generate_recap()

Input:  transcription.txt
   │
   ├─► Send full transcript to GPT-4
   │
   ├─► AI analyzes:
   │   • Key moments
   │   • Emotional peaks
   │   • Story flow
   │   • Impact points
   │
   ├─► AI generates:
   │   • Recap text (30s narration)
   │   • Clip timings (start/end)
   │   • Reasons for each clip
   │
   └─► Output: recap_data.json + recap_text.txt

Example recap_data.json:
{
  "recap_text": "A rollercoaster of emotions...",
  "clip_timings": [
    {"start": 0, "end": 5, "reason": "Opening statement"},
    {"start": 19, "end": 22, "reason": "Emotional peak"},
    {"start": 34, "end": 37, "reason": "Powerful conclusion"}
  ],
  "total_duration": 30
}
```

### Step 4: Video Clip Extraction 🎬
```
Function: extract_video_clips()

Input:  video_file.mp4 + recap_data.json
   │
   ├─► Load original video (MoviePy)
   │
   ├─► For each clip timing:
   │   │
   │   ├─► Extract subclip(start, end)
   │   ├─► Store in clips array
   │   └─► Log progress
   │
   ├─► Concatenate all clips
   │
   ├─► Render final video
   │   • Codec: H.264
   │   • Audio: AAC
   │   • Method: compose
   │
   └─► Output: recap_video.mp4

Processing Example:
[Clip 1] 0s-5s   ████████░░ (Opening)
[Clip 2] 19s-22s ████████░░ (Peak moment)
[Clip 3] 34s-37s ████████░░ (Conclusion)
         ↓
    [Final Video] 30 seconds
```

## Agent Interaction Flow

```
┌──────────────────────────────────────────────────────────┐
│  User initiates chat with video parameters               │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│  Chatbot Agent receives task:                            │
│  "Transcribe → Translate → Generate Recap → Extract"     │
└────────────────────┬─────────────────────────────────────┘
                     │
    ┌────────────────┴────────────────┐
    │                                 │
    ▼                                 ▼
┌─────────────┐              ┌────────────────┐
│  Chatbot    │              │  User Proxy    │
│  Decides:   │──Function───►│  Executes:     │
│  Which      │    Call      │  Actual        │
│  function   │              │  function      │
│  to call    │◄───Result────│  code          │
└─────────────┘              └────────────────┘
    │                                 │
    │          Repeat until           │
    │          all tasks done         │
    │                                 │
    └────────────┬────────────────────┘
                 │
                 ▼
    ┌────────────────────────┐
    │  Agent replies:        │
    │  "TERMINATE"           │
    └────────────────────────┘
```

## Key Features

### 🎯 AI-Powered Clip Selection
The GPT-4 model analyzes:
- **Emotional intensity** of each segment
- **Narrative importance** in context
- **Visual/audio quality** indicators
- **Flow and transitions** between clips

### ⚡ Smart Duration Management
- Target duration: 30 seconds (configurable)
- AI ensures clips don't exceed target
- Natural pacing and transitions
- Maintains story coherence

### 🎨 Quality Preservation
- Original video resolution maintained
- Audio sync preserved
- No re-encoding quality loss
- Professional-grade output

## File Dependencies

```
Required for Recap Generation:
├── transcription.txt (from Step 1)
├── Original video file
└── .env (with OPENAI_API_KEY)

Generated Files:
├── recap_data.json (AI suggestions)
├── recap_text.txt (narration)
└── recap_video.mp4 (final output)
```

## Error Handling

```python
Try-Catch Coverage:
├── File not found (video, transcription)
├── JSON parsing errors
├── API failures (OpenAI)
├── Video processing errors (MoviePy)
└── Invalid timestamps

All errors return user-friendly messages
Autogen displays errors to user
No silent failures
```

## Performance Considerations

| Task                  | Time (approx) | Resource      |
|-----------------------|---------------|---------------|
| Transcription (1 min) | 30-60s        | CPU + 2GB RAM |
| Translation (10 lines)| 5-10s         | API call      |
| Recap Generation      | 10-20s        | API call      |
| Video Extraction (30s)| 15-30s        | CPU + Disk I/O|

**Total time for 1-minute video**: ~1-2 minutes

## Example Use Cases

### 1. Social Media Content
- Create teasers from long videos
- Instagram/TikTok-ready recaps
- Highlight reels

### 2. Meeting Summaries
- Extract key discussion points
- Share decision highlights
- Quick team updates

### 3. Educational Content
- Course teasers
- Concept summaries
- Preview clips

### 4. Entertainment
- Movie/show highlights
- Event recaps
- Compilation videos

## Future Enhancements

- [ ] Custom duration (not just 30s)
- [ ] Multiple recap styles (dramatic, informative, humorous)
- [ ] Add text overlays to recap
- [ ] Background music integration
- [ ] Transition effects between clips
- [ ] Batch processing multiple videos
- [ ] Export to different resolutions
- [ ] Social media format presets (square, vertical)

---

**Powered by AI • Built with Python • Optimized for Quality**

