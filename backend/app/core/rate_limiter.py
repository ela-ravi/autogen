import time

import redis
from fastapi import Depends, HTTPException, Request, status

from app.config import settings

TIER_RATE_LIMITS = {
    "free": {"requests": 10, "window": 60},       # 10 req/min
    "pro": {"requests": 60, "window": 60},         # 60 req/min
    "enterprise": {"requests": 300, "window": 60},  # 300 req/min
}

_redis = redis.from_url(settings.REDIS_URL)


class RateLimiter:
    def __init__(self, tier: str = "free"):
        self.tier = tier

    def check(self, user_id: str) -> tuple[bool, int, float]:
        """Returns (allowed, remaining, reset_at)."""
        limits = TIER_RATE_LIMITS.get(self.tier, TIER_RATE_LIMITS["free"])
        max_requests = limits["requests"]
        window = limits["window"]

        now = time.time()
        key = f"ratelimit:{user_id}"

        pipe = _redis.pipeline()
        pipe.zremrangebyscore(key, 0, now - window)
        pipe.zadd(key, {str(now): now})
        pipe.zcard(key)
        pipe.expire(key, window)
        results = pipe.execute()

        current_count = results[2]
        allowed = current_count <= max_requests
        remaining = max(0, max_requests - current_count)
        reset_at = now + window

        return allowed, remaining, reset_at


async def rate_limit_dependency(request: Request):
    """FastAPI dependency that enforces rate limiting."""
    user = getattr(request.state, "user", None)
    if not user:
        return

    tier = getattr(user, "tier", "free")
    limiter = RateLimiter(tier)
    allowed, remaining, reset_at = limiter.check(user.id)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(int(reset_at)),
            },
        )
