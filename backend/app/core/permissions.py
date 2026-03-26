from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.usage import UsageRecord

TIER_QUOTAS = {
    "free": 3,
    "pro": 50,
    "enterprise": -1,  # Unlimited
}


async def check_quota(db: AsyncSession, user_id: str, tier: str):
    """Raise 429 if user has exceeded their monthly recap quota."""
    if not settings.ENABLE_BILLING:
        return

    quota = TIER_QUOTAS.get(tier, 3)
    if quota == -1:
        return  # Unlimited

    today = date.today()
    period_start = today.replace(day=1)

    result = await db.execute(
        select(func.count())
        .select_from(UsageRecord)
        .where(
            UsageRecord.user_id == user_id,
            UsageRecord.period_start == period_start,
            UsageRecord.action == "recap_created",
        )
    )
    usage_count = result.scalar()

    if usage_count >= quota:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Monthly quota exceeded ({usage_count}/{quota}). Upgrade your plan for more recaps.",
            headers={"X-Quota-Used": str(usage_count), "X-Quota-Limit": str(quota)},
        )
