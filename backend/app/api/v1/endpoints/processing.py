"""User-facing processing controls (e.g. worker-side cache invalidation)."""

import redis
from fastapi import APIRouter, Depends

from app.api.v1.deps import get_current_user
from app.config import settings
from app.models.user import User
from modules.transcription import WHISPER_CACHE_REDIS_KEY

router = APIRouter(prefix="/processing", tags=["processing"])


@router.post("/clear-whisper-cache")
async def clear_whisper_cache(_current_user: User = Depends(get_current_user)):
    """
    Bump a Redis generation counter so every Celery worker process drops its in-memory
    Whisper model on the next transcription. Use if consecutive jobs fail in odd ways.
    """
    r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        generation = r.incr(WHISPER_CACHE_REDIS_KEY)
    finally:
        r.close()
    return {
        "detail": "Whisper model cache will reload on the next transcription on each worker.",
        "generation": generation,
    }
