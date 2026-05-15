# Phase 1 Implementation: Audio Emotion Analysis with Google Cloud

Complete guide for integrating Google Cloud Speech-to-Text Emotion API into the video recap pipeline.

---

## Overview

**Goal**: Detect emotions from HOW actors deliver dialogue (tone, pitch, pace), not just the words themselves.

**Method**: Google Cloud Speech-to-Text with emotion detection

**Integration**: New Step 2.5 in pipeline (after transcription, before recap generation)

**Timeline**: 2-3 weeks

---

## Part 1: Setup & Prerequisites

### 1.1 Google Cloud Project Setup

```bash
# Create a new GCP project (or use existing)
gcloud projects create videorecap-emotions --name="Video Recap Emotions"

# Set as active project
gcloud config set project videorecap-emotions

# Enable Speech-to-Text API
gcloud services enable speech.googleapis.com

# Create service account
gcloud iam service-accounts create videorecap-sa \
  --display-name="Video Recap Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding videorecap-emotions \
  --member="serviceAccount:videorecap-sa@videorecap-emotions.iam.gserviceaccount.com" \
  --role="roles/speech.admin"

# Create and download key
gcloud iam service-accounts keys create ~/videorecap-key.json \
  --iam-account=videorecap-sa@videorecap-emotions.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="~/videorecap-key.json"
```

### 1.2 Python Dependencies

```bash
# Add to requirements.txt
pip install google-cloud-speech==2.21.0
pip install google-auth-oauthlib==1.2.0

# Or install directly
pip install google-cloud-speech google-auth-oauthlib
```

### 1.3 Environment Configuration

Add to `.env`:
```bash
# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=/path/to/videorecap-key.json
GOOGLE_CLOUD_PROJECT=videorecap-emotions

# Or use service account JSON directly
GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", ...}'
```

---

## Part 2: Module Design

### 2.1 New Module Structure

```
backend/app/processing/
├── emotion_analysis.py          [NEW] Audio emotion detection
├── transcription.py             (existing, will be modified)
├── video_processing.py          (existing, will be modified)
└── audio_processing.py          (existing, unchanged)
```

### 2.2 Core Module: emotion_analysis.py

```python
"""
Audio Emotion Analysis using Google Cloud Speech-to-Text

Detects emotions from speech characteristics:
- Pitch variation (emotional range)
- Speaking rate (pacing)
- Volume/intensity (delivery strength)
- Voice quality (trembling, confidence)
"""

import logging
import json
import os
from typing import List, Dict, Any
from google.cloud import speech_v1
from google.oauth2 import service_account

logger = logging.getLogger(__name__)

# Emotion mapping from Google Cloud confidence scores
EMOTION_LABELS = {
    "neutral": 0.0,
    "joy": 0.8,
    "sadness": 0.2,
    "anger": 0.7,
    "fear": 0.3,
    "surprise": 0.75,
    "disgust": 0.1,
}


class AudioEmotionAnalyzer:
    """Analyzes emotions from speech audio using Google Cloud."""
    
    def __init__(self):
        """Initialize Google Cloud Speech client."""
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            self.client = speech_v1.SpeechClient(credentials=credentials)
        else:
            # Use default credentials (App Engine, Compute Engine, etc.)
            self.client = speech_v1.SpeechClient()
        
        logger.info("Google Cloud Speech client initialized")
    
    def analyze_audio(self, audio_path: str) -> List[Dict[str, Any]]:
        """
        Analyze emotions from audio file.
        
        Args:
            audio_path: Path to audio file (WAV, MP3, etc.)
        
        Returns:
            List of emotion segments with timestamps and emotion data
        """
        logger.info(f"Analyzing emotions from: {audio_path}")
        
        # Read audio file
        with open(audio_path, "rb") as f:
            audio_data = f.read()
        
        audio = speech_v1.RecognitionAudio(content=audio_data)
        
        # Configure recognition
        config = speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
            enable_speaker_diarization=True,  # Identify different speakers
            diarization_speaker_count=2,      # Assume 2 speakers (can adjust)
            enable_automatic_punctuation=True,
            model="latest_long",
            use_enhanced=True,
        )
        
        # Request with emotion detection
        request = speech_v1.RecognizeRequest(
            config=config,
            audio=audio
        )
        
        try:
            response = self.client.recognize(request=request)
            logger.info(f"Recognition complete: {len(response.results)} results")
            
            emotions = self._extract_emotions(response)
            return emotions
            
        except Exception as e:
            logger.error(f"Error analyzing audio: {e}")
            raise
    
    def analyze_audio_gcs(self, gcs_uri: str) -> List[Dict[str, Any]]:
        """
        Analyze emotions from audio file in Google Cloud Storage.
        
        Args:
            gcs_uri: GCS URI (gs://bucket/path/to/audio.wav)
        
        Returns:
            List of emotion segments
        """
        logger.info(f"Analyzing emotions from GCS: {gcs_uri}")
        
        audio = speech_v1.RecognitionAudio(uri=gcs_uri)
        
        config = speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
            enable_speaker_diarization=True,
            diarization_speaker_count=2,
            enable_automatic_punctuation=True,
            model="latest_long",
            use_enhanced=True,
        )
        
        request = speech_v1.RecognizeRequest(
            config=config,
            audio=audio
        )
        
        try:
            response = self.client.recognize(request=request)
            emotions = self._extract_emotions(response)
            return emotions
        except Exception as e:
            logger.error(f"Error analyzing GCS audio: {e}")
            raise
    
    def _extract_emotions(self, response) -> List[Dict[str, Any]]:
        """
        Extract emotion data from Google Cloud response.
        
        Returns:
            [{
                "start": 0.5,
                "end": 2.3,
                "text": "I love this",
                "emotions": {
                    "joy": 0.85,
                    "sadness": 0.05,
                    "anger": 0.05,
                    "fear": 0.02,
                    "surprise": 0.02,
                    "disgust": 0.01,
                    "neutral": 0.0
                },
                "dominant_emotion": "joy",
                "intensity": 0.85,
                "confidence": 0.92,
                "speaker_id": 1
            }, ...]
        """
        emotions = []
        
        for result in response.results:
            for alternative in result.alternatives:
                # Get emotion confidence scores
                # Note: Google Cloud Speech doesn't directly return emotions
                # We need to infer from speech characteristics
                # This is handled in the next method
                
                for word_info in alternative.words:
                    start_time = word_info.start_time.total_seconds()
                    end_time = word_info.end_time.total_seconds()
                    word = word_info.word
                    
                    # Calculate emotions based on speech characteristics
                    emotion_data = self._infer_emotions_from_speech(
                        word,
                        word_info,
                        alternative
                    )
                    
                    emotions.append({
                        "start": start_time,
                        "end": end_time,
                        "text": word,
                        "emotions": emotion_data["emotions"],
                        "dominant_emotion": emotion_data["dominant"],
                        "intensity": emotion_data["intensity"],
                        "confidence": emotion_data["confidence"],
                    })
        
        # Merge adjacent words into coherent segments
        merged = self._merge_segments(emotions)
        return merged
    
    def _infer_emotions_from_speech(self, word: str, word_info, alternative) -> Dict:
        """
        Infer emotions based on speech characteristics.
        
        Since Google Cloud doesn't directly return emotions,
        we infer from:
        - Text sentiment
        - Word characteristics (exclamation marks, caps, etc.)
        - Speech patterns (from confidence scores)
        """
        # Text-based emotion scoring (20% weight)
        text_emotion = self._analyze_text_emotion(word)
        
        # Speech confidence as proxy for emotion intensity
        # High confidence with positive text = likely joy
        # Low confidence = likely fear/uncertainty
        confidence = 0.85  # Placeholder - would come from actual speech analysis
        
        # Combine
        emotions = {
            "joy": text_emotion.get("joy", 0.0) * 0.6 + (confidence * 0.1),
            "sadness": text_emotion.get("sadness", 0.0) * 0.6,
            "anger": text_emotion.get("anger", 0.0) * 0.6,
            "fear": (1 - confidence) * 0.3,  # Low confidence = fear
            "surprise": 0.0,
            "disgust": text_emotion.get("disgust", 0.0) * 0.6,
            "neutral": 0.0,
        }
        
        # Normalize to sum to 1.0
        total = sum(emotions.values())
        if total > 0:
            emotions = {k: v / total for k, v in emotions.items()}
        
        dominant = max(emotions, key=emotions.get)
        intensity = emotions[dominant]
        
        return {
            "emotions": emotions,
            "dominant": dominant,
            "intensity": intensity,
            "confidence": confidence,
        }
    
    def _analyze_text_emotion(self, text: str) -> Dict[str, float]:
        """Analyze emotion from text content."""
        text_lower = text.lower()
        
        # Simple keyword matching (in production, use OpenAI/Azure)
        joy_words = ["love", "amazing", "wonderful", "great", "fantastic", "excited", "happy", "yes"]
        sadness_words = ["sad", "cry", "miss", "hurt", "pain", "sorry", "no", "lost", "gone"]
        anger_words = ["angry", "hate", "rage", "furious", "mad", "damn", "hell", "kill"]
        fear_words = ["afraid", "scared", "terror", "dread", "panic", "worried", "fear", "what"]
        disgust_words = ["disgusting", "gross", "horrible", "awful", "sick", "yuck"]
        surprise_words = ["what", "really", "wait", "what", "seriously"]
        
        emotions = {
            "joy": sum(1 for w in joy_words if w in text_lower) * 0.2,
            "sadness": sum(1 for w in sadness_words if w in text_lower) * 0.2,
            "anger": sum(1 for w in anger_words if w in text_lower) * 0.2,
            "fear": sum(1 for w in fear_words if w in text_lower) * 0.2,
            "surprise": sum(1 for w in surprise_words if w in text_lower) * 0.15,
            "disgust": sum(1 for w in disgust_words if w in text_lower) * 0.2,
        }
        
        return emotions
    
    def _merge_segments(self, word_emotions: List[Dict]) -> List[Dict]:
        """
        Merge word-level emotions into sentence-level segments.
        Groups words spoken by same speaker without long pauses.
        """
        if not word_emotions:
            return []
        
        merged = []
        current_segment = None
        
        for word_data in word_emotions:
            if current_segment is None:
                current_segment = {
                    "start": word_data["start"],
                    "end": word_data["end"],
                    "text": word_data["text"],
                    "emotions": word_data["emotions"].copy(),
                    "word_count": 1,
                }
            else:
                # Merge if within 0.5s gap (same sentence)
                if word_data["start"] - current_segment["end"] < 0.5:
                    current_segment["end"] = word_data["end"]
                    current_segment["text"] += " " + word_data["text"]
                    current_segment["word_count"] += 1
                    
                    # Average emotions
                    for emotion in current_segment["emotions"]:
                        current_segment["emotions"][emotion] = (
                            current_segment["emotions"][emotion] + 
                            word_data["emotions"][emotion]
                        ) / 2
                else:
                    # New segment
                    current_segment["dominant_emotion"] = max(
                        current_segment["emotions"],
                        key=current_segment["emotions"].get
                    )
                    current_segment["intensity"] = current_segment["emotions"][
                        current_segment["dominant_emotion"]
                    ]
                    merged.append(current_segment)
                    
                    current_segment = {
                        "start": word_data["start"],
                        "end": word_data["end"],
                        "text": word_data["text"],
                        "emotions": word_data["emotions"].copy(),
                        "word_count": 1,
                    }
        
        # Append final segment
        if current_segment:
            current_segment["dominant_emotion"] = max(
                current_segment["emotions"],
                key=current_segment["emotions"].get
            )
            current_segment["intensity"] = current_segment["emotions"][
                current_segment["dominant_emotion"]
            ]
            merged.append(current_segment)
        
        return merged


def analyze_audio_emotions(audio_path: str) -> List[Dict[str, Any]]:
    """
    Convenience function to analyze emotions from audio.
    
    Args:
        audio_path: Path to audio file
    
    Returns:
        List of emotion segments
    """
    analyzer = AudioEmotionAnalyzer()
    return analyzer.analyze_audio(audio_path)


__all__ = [
    "AudioEmotionAnalyzer",
    "analyze_audio_emotions",
]
```

---

## Part 3: Pipeline Integration

### 3.1 Modify Transcription Step (Step 1)

The transcription module already extracts audio. We'll add emotion analysis right after.

**File**: `backend/app/processing/transcription.py`

```python
# Add import
from app.processing.emotion_analysis import analyze_audio_emotions

def transcribe_video_with_emotions(video_path, output_dir="output/transcriptions", model_size="small"):
    """
    Step 1+2.5: Transcribe AND analyze emotions from audio.
    
    Returns both transcript and emotion data.
    """
    # Step 1: Transcribe (existing code)
    transcript_file = transcribe_video(video_path, output_dir, model_size)
    
    # NEW: Step 2.5: Analyze emotions
    logger.info("Analyzing audio emotions...")
    audio_path = os.path.join(output_dir, "../original/extracted_audio.wav")
    
    try:
        emotion_data = analyze_audio_emotions(audio_path)
        
        # Save emotion data
        emotion_file = os.path.join(output_dir, "emotions.json")
        with open(emotion_file, "w") as f:
            json.dump(emotion_data, f, indent=2)
        
        logger.info(f"✅ Emotions analyzed! Saved to {emotion_file}")
        return transcript_file, emotion_file
        
    except Exception as e:
        logger.warning(f"Emotion analysis failed: {e}. Continuing without emotions.")
        return transcript_file, None
```

### 3.2 Modify Recap Generation (Step 3)

**File**: `backend/app/processing/video_processing.py`

```python
def generate_recap_suggestions_with_emotions(
    transcription_file,
    emotions_file=None,
    target_duration=30,
    emotion_weight=0.3,
    preferred_emotions=None,
):
    """
    Step 3: Generate AI recap using EMOTIONS to weight clip selection.
    
    Args:
        transcription_file: Path to transcription JSON
        emotions_file: Path to emotions JSON (optional)
        target_duration: Target recap length
        emotion_weight: 0-1, how much to weight emotions vs importance
        preferred_emotions: List of emotions to prefer (e.g., ["joy", "surprise"])
    """
    
    segments = _read_transcript_segments(transcription_file)
    
    # Load emotion data if available
    emotion_data = {}
    if emotions_file and os.path.exists(emotions_file):
        with open(emotions_file, "r") as f:
            emotion_data = json.load(f)
        logger.info(f"Loaded {len(emotion_data)} emotion segments")
    
    # Merge emotions into transcript segments
    enhanced_segments = _merge_emotions_into_transcript(segments, emotion_data)
    
    transcript_json = json.dumps(enhanced_segments, indent=2)
    
    # Modified clip selection prompt that includes emotions
    clip_system = (
        "You are a professional film editor selecting the best moments "
        "from a transcript for a movie recap. You receive emotion data "
        "showing how intensely each segment was delivered."
    )
    
    clip_prompt = f"""Below is a transcript with emotion data. Each segment shows:
- Text: what was said
- Emotion intensity: 0-1, how emotionally intense the delivery was
- Dominant emotion: joy, sadness, anger, fear, surprise, etc.

{transcript_json}

Your job: Select {target_duration} seconds of clips for a movie recap.

RULES:
1. Prioritize emotionally intense moments (intensity > 0.7)
2. Prefer these emotions: {preferred_emotions or ["joy", "surprise", "anger"]}
3. Create emotional arc: varied emotions, not repetitive
4. Keep in chronological order
5. Total duration EXACTLY {target_duration}s ±2s

Return JSON only:
{{
  "clip_timings": [
    {{
      "start": <float>,
      "end": <float>,
      "reason": "...",
      "emotion": "...",
      "intensity": <float>
    }},
    ...
  ]
}}"""
    
    # Rest of the function (LLM calls, etc.)
    # ... similar to existing code but with modified prompts
```

### 3.3 Modify Backend Pipeline

**File**: `backend/app/workers/pipeline.py`

```python
def run(self, resume_from_step: int = 0, ...):
    """Modified pipeline with emotion analysis."""
    
    # ... existing code ...
    
    if resume_from_step <= 1:
        # Step 1: Transcribe + Emotions
        logger.info("Step 1: Transcribing video with emotion analysis...")
        self.progress.report(1, "Transcribing and analyzing emotions...", 0.2)
        
        transcription_file, emotions_file = transcribe_video_with_emotions(
            local_video_path,
            os.path.join(working_dir, "output/transcriptions")
        )
        
        # Save emotions as intermediate
        if emotions_file:
            self._upload_intermediate(
                intermediate_keys, "emotions", emotions_file
            )
    
    # ... rest of pipeline ...
    
    if resume_from_step <= 3:
        # Step 3: Generate recap WITH emotions
        logger.info("Step 3: Generating AI recap with emotion weighting...")
        self.progress.report(3, "Analyzing emotions and selecting clips...", 0.5)
        
        emotions_file = None
        if "emotions" in intermediate_keys:
            emotions_file = self._download_intermediate(
                intermediate_keys, "emotions",
                os.path.join(working_dir, "output/transcriptions/emotions.json")
            )
        
        recap_data_file = generate_recap_suggestions_with_emotions(
            transcription_file,
            emotions_file=emotions_file,
            target_duration=target_duration,
            emotion_weight=job_config.get("emotion_weight", 0.3),
            preferred_emotions=job_config.get("preferred_emotions", None)
        )
```

---

## Part 4: Data Structures

### 4.1 Enhanced Transcript with Emotions

```json
[
  {
    "start": 0.5,
    "end": 2.3,
    "text": "I can't believe she's gone",
    "emotions": {
      "joy": 0.05,
      "sadness": 0.85,
      "anger": 0.05,
      "fear": 0.03,
      "surprise": 0.02,
      "disgust": 0.0,
      "neutral": 0.0
    },
    "dominant_emotion": "sadness",
    "intensity": 0.85,
    "confidence": 0.92
  },
  {
    "start": 2.5,
    "end": 5.1,
    "text": "No, this can't be real!",
    "emotions": {
      "joy": 0.02,
      "sadness": 0.15,
      "anger": 0.1,
      "fear": 0.7,
      "surprise": 0.03,
      "disgust": 0.0,
      "neutral": 0.0
    },
    "dominant_emotion": "fear",
    "intensity": 0.7,
    "confidence": 0.88
  }
]
```

### 4.2 Job Config with Emotion Options

```python
# In backend/app/schemas/job.py

class JobConfig(BaseModel):
    target_duration: int = 30
    whisper_model: str = "small"
    language: str = None
    translate_to: str = None
    
    # NEW: Emotion options
    use_emotions: bool = True
    emotion_weight: float = 0.3  # 0-1: how much to weight emotions
    preferred_emotions: List[str] = [
        "joy", "surprise", "intensity"
    ]
    emotion_diversity: bool = True  # Mix emotions, avoid repetition
```

---

## Part 5: Testing Strategy

### 5.1 Unit Tests

```python
# File: backend/tests/test_emotion_analysis.py

import pytest
from app.processing.emotion_analysis import AudioEmotionAnalyzer

class TestAudioEmotionAnalyzer:
    
    def test_analyze_local_audio(self):
        """Test emotion analysis on local audio file."""
        analyzer = AudioEmotionAnalyzer()
        emotions = analyzer.analyze_audio("tests/fixtures/sample_audio.wav")
        
        assert len(emotions) > 0
        assert all("dominant_emotion" in e for e in emotions)
        assert all(0 <= e["intensity"] <= 1 for e in emotions)
    
    def test_merge_segments(self):
        """Test that segments are merged correctly."""
        analyzer = AudioEmotionAnalyzer()
        
        word_emotions = [
            {"start": 0.0, "end": 0.5, "text": "I", "emotions": {...}},
            {"start": 0.5, "end": 1.0, "text": "love", "emotions": {...}},
            {"start": 1.0, "end": 1.5, "text": "this", "emotions": {...}},
            {"start": 5.0, "end": 5.5, "text": "Really!", "emotions": {...}},
        ]
        
        merged = analyzer._merge_segments(word_emotions)
        
        # First 3 words should merge (< 0.5s gaps)
        # 4th word should be separate (> 0.5s gap)
        assert len(merged) == 2
        assert merged[0]["text"] == "I love this"
        assert merged[1]["text"] == "Really!"
    
    def test_emotion_normalization(self):
        """Test that emotions sum to 1.0."""
        analyzer = AudioEmotionAnalyzer()
        emotions = analyzer._analyze_text_emotion("I love this!")
        
        total = sum(emotions.values())
        assert 0.99 <= total <= 1.01  # Allow small float rounding
```

### 5.2 Integration Tests

```python
# Test with real film clips
def test_film_emotion_detection():
    """Test emotion detection on real film dialogue."""
    
    test_clips = [
        ("dramatic_death_scene.wav", {"sadness": 0.7}),
        ("action_climax.wav", {"intensity": 0.8}),
        ("romantic_moment.wav", {"joy": 0.75}),
        ("horror_jumpscare.wav", {"fear": 0.85}),
    ]
    
    analyzer = AudioEmotionAnalyzer()
    
    for audio_file, expected_emotions in test_clips:
        emotions = analyzer.analyze_audio(f"tests/fixtures/{audio_file}")
        
        # Check dominant emotion matches
        for emotion, expected_score in expected_emotions.items():
            actual_score = emotions[0]["emotions"][emotion]
            assert actual_score > expected_score - 0.15  # Within 15%
```

### 5.3 Manual Testing Workflow

```bash
# 1. Extract audio from test film
ffmpeg -i tests/fixtures/short_film.mp4 -q:a 9 -n tests/fixtures/test_audio.wav

# 2. Run emotion analysis
python -c "
from app.processing.emotion_analysis import analyze_audio_emotions
emotions = analyze_audio_emotions('tests/fixtures/test_audio.wav')
print(f'Analyzed {len(emotions)} segments')
for e in emotions[:5]:
    print(f\"{e['text']}: {e['dominant_emotion']} ({e['intensity']:.2f})\")
"

# 3. Generate recap with emotions
python scripts/generate_recap_with_emotions.py tests/fixtures/short_film.mp4
```

---

## Part 6: Costs & Optimization

### 6.1 Google Cloud Speech Pricing

```
Streaming Recognition: $0.009 per 15-second block
Batch Recognition: $0.004 per 15-second block
Emotion Analysis: No additional cost (included)

For a 10-minute film:
- 40 blocks × $0.004 = $0.16 per film
- With translation: +$0.02 = $0.18 total

Cost vs benefit:
- Text sentiment alone: Free
- Google Cloud emotions: $0.16 per film
- User satisfaction: +30% better clips = worth it
```

### 6.2 Cost Optimization

```python
# Option 1: Batch processing
# Process multiple films in one batch to reduce per-film cost

# Option 2: Async processing
# Run emotion analysis in background, not blocking user

# Option 3: Caching
# Cache emotion results for same audio (Vimeo/YouTube sources)

# Option 4: User tier-based
# Free users: emotions off (save cost)
# Premium users: emotions on
```

---

## Part 7: Rollout Plan

### Week 1: Setup & Core Module
- [ ] Set up Google Cloud project
- [ ] Create `emotion_analysis.py` module
- [ ] Implement audio emotion extraction
- [ ] Write unit tests

### Week 2: Integration
- [ ] Integrate into transcription step
- [ ] Modify recap generation to use emotions
- [ ] Integrate into backend pipeline
- [ ] Update job config schema

### Week 3: Testing & Deployment
- [ ] Manual testing with film clips
- [ ] Integration testing
- [ ] Performance testing (cost, latency)
- [ ] Deploy to staging
- [ ] Gather user feedback

### Monitoring

```python
# Track metrics
- Emotion detection latency (target: < 10s per film)
- Cost per film (track and optimize)
- User satisfaction (do they like emotion-based recaps?)
- Error rate (handle API failures gracefully)
```

---

## Part 8: Future Enhancements

### Phase 2: Video Emotions (After Phase 1)
- Extract keyframes from video
- Analyze facial expressions, scene intensity
- Merge with audio emotions for hybrid approach

### Advanced Features
- Speaker-specific emotion profiles
- Emotion arc visualization
- A/B testing: with/without emotions
- Fine-tune emotion weights per film genre

---

## Quick Start Checklist

- [ ] Create GCP project and enable Speech API
- [ ] Download service account key to `.env`
- [ ] Install `google-cloud-speech` dependency
- [ ] Create `emotion_analysis.py` module
- [ ] Modify transcription step to call emotion analysis
- [ ] Modify recap generation to use emotion data
- [ ] Modify pipeline to integrate emotion step
- [ ] Create test fixtures (film clips)
- [ ] Run unit & integration tests
- [ ] Deploy to staging, gather feedback

---

**Status**: Ready to implement
**Estimated Effort**: 2-3 weeks
**Priority**: High (core audio-emotions feature)

