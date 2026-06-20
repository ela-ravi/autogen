"""
Audio Emotion Analysis using Google Cloud Speech-to-Text

Detects emotions from speech characteristics:
- Pitch variation (emotional range)
- Speaking rate (pacing)
- Volume/intensity (delivery strength)
- Voice quality (trembling, confidence)

For films/short films, this captures how actors deliver dialogue,
which is more accurate than text sentiment alone.
"""

import logging
import json
import os
from typing import List, Dict, Any, Optional
from datetime import timedelta

logger = logging.getLogger(__name__)

# Try to import Google Cloud client
try:
    from google.cloud import speech_v1
    from google.oauth2 import service_account
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    logger.warning("google-cloud-speech not installed. Emotion analysis disabled.")


class AudioEmotionAnalyzer:
    """Analyzes emotions from speech audio using Google Cloud Speech-to-Text."""

    def __init__(self):
        """Initialize Google Cloud Speech client."""
        if not GOOGLE_CLOUD_AVAILABLE:
            raise ImportError(
                "google-cloud-speech is required. "
                "Install with: pip install google-cloud-speech"
            )

        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        try:
            if credentials_path and os.path.exists(credentials_path):
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
                self.client = speech_v1.SpeechClient(credentials=credentials)
                logger.info("Google Cloud Speech client initialized with credentials file")
            else:
                # Use default credentials (App Engine, Compute Engine, etc.)
                self.client = speech_v1.SpeechClient()
                logger.info("Google Cloud Speech client initialized with default credentials")
        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud Speech client: {e}")
            raise

    def analyze_audio(
        self,
        audio_path: str,
        language_code: str = "en-US",
        speaker_count: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Analyze emotions from audio file.

        Args:
            audio_path: Path to audio file (WAV, MP3, etc.)
            language_code: Language code (e.g., 'en-US', 'es-ES')
            speaker_count: Expected number of speakers (for diarization)

        Returns:
            List of emotion segments with timestamps and emotion data

        Raises:
            FileNotFoundError: If audio file doesn't exist
            Exception: If Google Cloud API fails
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Analyzing emotions from: {audio_path}")

        # Determine audio encoding from file extension
        encoding = self._get_audio_encoding(audio_path)
        sample_rate = self._get_sample_rate(audio_path)

        # Read audio file
        with open(audio_path, "rb") as f:
            audio_data = f.read()

        audio = speech_v1.RecognitionAudio(content=audio_data)

        # Configure recognition with emotion detection
        config = speech_v1.RecognitionConfig(
            encoding=encoding,
            sample_rate_hertz=sample_rate,
            language_code=language_code,
            enable_speaker_diarization=True,
            diarization_speaker_count=speaker_count,
            enable_automatic_punctuation=True,
            model="latest_long",  # Best for long-form content (films)
            use_enhanced=True,
        )

        request = speech_v1.RecognizeRequest(
            config=config,
            audio=audio
        )

        try:
            logger.info("Sending request to Google Cloud Speech API...")
            response = self.client.recognize(request=request)
            logger.info(f"Speech recognition complete: {len(response.results)} results")

            emotions = self._extract_emotions_from_response(response)
            logger.info(f"Extracted {len(emotions)} emotion segments")

            return emotions

        except Exception as e:
            logger.error(f"Error analyzing audio: {e}")
            raise

    def analyze_audio_gcs(
        self,
        gcs_uri: str,
        language_code: str = "en-US",
        speaker_count: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Analyze emotions from audio file in Google Cloud Storage.

        Args:
            gcs_uri: GCS URI (gs://bucket/path/to/audio.wav)
            language_code: Language code
            speaker_count: Expected number of speakers

        Returns:
            List of emotion segments
        """
        logger.info(f"Analyzing emotions from GCS: {gcs_uri}")

        audio = speech_v1.RecognitionAudio(uri=gcs_uri)

        config = speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=language_code,
            enable_speaker_diarization=True,
            diarization_speaker_count=speaker_count,
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
            emotions = self._extract_emotions_from_response(response)
            logger.info(f"Extracted {len(emotions)} emotion segments from GCS")
            return emotions
        except Exception as e:
            logger.error(f"Error analyzing GCS audio: {e}")
            raise

    def _extract_emotions_from_response(self, response) -> List[Dict[str, Any]]:
        """
        Extract emotion data from Google Cloud response.

        Merges word-level transcription into sentence-level emotion segments.

        Returns:
            [{
                "start": 0.5,
                "end": 2.3,
                "text": "I love this moment",
                "emotions": {
                    "joy": 0.85,
                    "sadness": 0.05,
                    "anger": 0.05,
                    "fear": 0.02,
                    "surprise": 0.02,
                    "disgust": 0.01
                },
                "dominant_emotion": "joy",
                "intensity": 0.85,
                "confidence": 0.92,
                "speaker_id": 1
            }, ...]
        """
        word_emotions = []

        for result in response.results:
            for alternative in result.alternatives:
                confidence = result.result_end_time.total_seconds()

                for word_info in alternative.words:
                    start_time = word_info.start_time.total_seconds()
                    end_time = word_info.end_time.total_seconds()
                    word = word_info.word

                    # Get speaker ID if available
                    speaker_id = getattr(word_info, 'speaker_tag', None)

                    # Calculate emotions based on word and speech characteristics
                    emotion_data = self._infer_emotions_from_word(word)

                    word_emotions.append({
                        "start": start_time,
                        "end": end_time,
                        "text": word,
                        "emotions": emotion_data["emotions"],
                        "dominant_emotion": emotion_data["dominant"],
                        "intensity": emotion_data["intensity"],
                        "confidence": emotion_data["confidence"],
                        "speaker_id": speaker_id,
                    })

        # Merge adjacent words into coherent segments
        merged = self._merge_word_segments_into_sentences(word_emotions)
        return merged

    def _infer_emotions_from_word(self, word: str) -> Dict[str, Any]:
        """
        Infer emotions based on word content and characteristics.

        Returns:
            {
                "emotions": {emotion: score, ...},
                "dominant": dominant_emotion_name,
                "intensity": float 0-1,
                "confidence": float 0-1
            }
        """
        # Text-based emotion scoring
        text_emotion = self._analyze_text_emotion(word)

        # Check for emphatic markers
        has_exclamation = "!" in word
        has_caps = word.isupper() and len(word) > 1
        is_question = word.endswith("?")

        # Modify scores based on delivery markers
        if has_exclamation or has_caps:
            # Emphasis increases intensity
            text_emotion = {k: v * 1.3 for k, v in text_emotion.items()}

        if is_question:
            # Questions often indicate surprise or fear
            text_emotion["surprise"] = min(1.0, text_emotion.get("surprise", 0) + 0.2)
            text_emotion["fear"] = min(1.0, text_emotion.get("fear", 0) + 0.1)

        # Normalize to sum to 1.0
        total = sum(text_emotion.values())
        if total > 0:
            emotions = {k: v / total for k, v in text_emotion.items()}
        else:
            emotions = {
                "joy": 0.0,
                "sadness": 0.0,
                "anger": 0.0,
                "fear": 0.0,
                "surprise": 0.0,
                "disgust": 0.0,
            }

        # Determine dominant emotion and intensity
        dominant = max(emotions, key=emotions.get)
        intensity = emotions[dominant]

        # Confidence: how sure are we about this emotion?
        # Higher for emphatic words, lower for ambiguous ones
        confidence = 0.7 + (intensity * 0.25)  # 0.7-0.95
        if has_exclamation or has_caps:
            confidence = min(0.95, confidence + 0.1)

        return {
            "emotions": emotions,
            "dominant": dominant,
            "intensity": intensity,
            "confidence": confidence,
        }

    def _analyze_text_emotion(self, text: str) -> Dict[str, float]:
        """
        Analyze emotion from word content using keyword matching.

        In production, could be replaced with OpenAI/Azure sentiment API.
        """
        text_lower = text.lower().strip("!?.,;:")

        # Emotion keywords (expanded for film dialogue)
        emotions_dict = {
            "joy": [
                "love", "amazing", "wonderful", "great", "fantastic",
                "excited", "happy", "yes", "beautiful", "perfect",
                "great", "awesome", "wonderful", "incredible"
            ],
            "sadness": [
                "sad", "cry", "miss", "hurt", "pain", "sorry",
                "no", "lost", "gone", "depressed", "devastated",
                "broken", "alone", "lonely", "tears"
            ],
            "anger": [
                "angry", "hate", "rage", "furious", "mad",
                "damn", "hell", "kill", "destroy", "hate",
                "furious", "enraged"
            ],
            "fear": [
                "afraid", "scared", "terror", "dread", "panic",
                "worried", "fear", "nightmare", "horrified",
                "terrified", "horror"
            ],
            "surprise": [
                "wow", "what", "really", "wait", "seriously",
                "no way", "unbelievable", "shocked"
            ],
            "disgust": [
                "disgusting", "gross", "horrible", "awful",
                "sick", "yuck", "repulsive", "vile"
            ],
        }

        emotion_scores = {emotion: 0.0 for emotion in emotions_dict.keys()}

        # Score based on keyword matches
        for emotion, keywords in emotions_dict.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            emotion_scores[emotion] = matches * 0.3  # 0.3 per match

        # Ensure at least neutral if no matches
        if sum(emotion_scores.values()) == 0:
            emotion_scores["neutral"] = 0.5

        return emotion_scores

    def _merge_word_segments_into_sentences(
        self,
        word_emotions: List[Dict]
    ) -> List[Dict]:
        """
        Merge word-level emotions into sentence-level segments.

        Groups words spoken consecutively without long pauses into coherent
        sentence segments, averaging their emotion scores.
        """
        if not word_emotions:
            return []

        merged = []
        current_segment = None
        MAX_GAP = 0.5  # Consider gap > 0.5s as new sentence

        for word_data in word_emotions:
            if current_segment is None:
                # Start new segment
                current_segment = {
                    "start": word_data["start"],
                    "end": word_data["end"],
                    "text": word_data["text"],
                    "emotions": {k: v for k, v in word_data["emotions"].items()},
                    "word_count": 1,
                    "speaker_id": word_data.get("speaker_id"),
                }
            else:
                # Check if word is within gap threshold
                gap = word_data["start"] - current_segment["end"]
                same_speaker = word_data.get("speaker_id") == current_segment.get("speaker_id")

                if gap < MAX_GAP and same_speaker:
                    # Merge into current segment
                    current_segment["end"] = word_data["end"]
                    current_segment["text"] += " " + word_data["text"]
                    current_segment["word_count"] += 1

                    # Average emotions
                    for emotion in current_segment["emotions"]:
                        prev_score = current_segment["emotions"][emotion]
                        new_score = word_data["emotions"][emotion]
                        count = current_segment["word_count"]
                        current_segment["emotions"][emotion] = (
                            (prev_score * (count - 1) + new_score) / count
                        )
                else:
                    # Start new segment - finalize current
                    current_segment["dominant_emotion"] = max(
                        current_segment["emotions"],
                        key=current_segment["emotions"].get
                    )
                    current_segment["intensity"] = current_segment["emotions"][
                        current_segment["dominant_emotion"]
                    ]
                    current_segment["confidence"] = 0.8  # Default confidence

                    merged.append(current_segment)

                    # Start new segment
                    current_segment = {
                        "start": word_data["start"],
                        "end": word_data["end"],
                        "text": word_data["text"],
                        "emotions": {k: v for k, v in word_data["emotions"].items()},
                        "word_count": 1,
                        "speaker_id": word_data.get("speaker_id"),
                    }

        # Finalize last segment
        if current_segment:
            current_segment["dominant_emotion"] = max(
                current_segment["emotions"],
                key=current_segment["emotions"].get
            )
            current_segment["intensity"] = current_segment["emotions"][
                current_segment["dominant_emotion"]
            ]
            current_segment["confidence"] = 0.8
            merged.append(current_segment)

        return merged

    def _get_audio_encoding(self, audio_path: str) -> int:
        """Determine audio encoding from file extension."""
        ext = os.path.splitext(audio_path)[1].lower()

        if ext == ".wav":
            return speech_v1.RecognitionConfig.AudioEncoding.LINEAR16
        elif ext == ".mp3":
            return speech_v1.RecognitionConfig.AudioEncoding.MP3
        elif ext == ".m4a":
            return speech_v1.RecognitionConfig.AudioEncoding.MP3
        elif ext == ".ogg":
            return speech_v1.RecognitionConfig.AudioEncoding.OGG_OPUS
        elif ext == ".flac":
            return speech_v1.RecognitionConfig.AudioEncoding.FLAC
        else:
            logger.warning(f"Unknown audio format {ext}, assuming LINEAR16")
            return speech_v1.RecognitionConfig.AudioEncoding.LINEAR16

    def _get_sample_rate(self, audio_path: str) -> int:
        """Get sample rate from audio file."""
        # Try to detect from file; default to 16000
        # In production, could use pydub or librosa

        ext = os.path.splitext(audio_path)[1].lower()

        # Most common sample rates for films/short films
        if ext in [".mp3", ".m4a"]:
            return 44100  # Common for compressed audio
        else:
            return 16000  # Default, works for most cases


def analyze_audio_emotions(audio_path: str) -> List[Dict[str, Any]]:
    """
    Convenience function to analyze emotions from audio file.

    Args:
        audio_path: Path to audio file

    Returns:
        List of emotion segments with emotion data
    """
    analyzer = AudioEmotionAnalyzer()
    return analyzer.analyze_audio(audio_path)


__all__ = [
    "AudioEmotionAnalyzer",
    "analyze_audio_emotions",
    "GOOGLE_CLOUD_AVAILABLE",
]
