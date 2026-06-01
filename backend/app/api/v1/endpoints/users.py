"""
User management endpoints - Development/Local utilities
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.api.v1.deps import get_current_user, get_db
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


class TierUpgradeResponse(BaseModel):
    message: str
    user_id: str
    email: str
    tier: str
    note: str | None = None


class UserInfoResponse(BaseModel):
    id: str
    email: str
    full_name: str
    tier: str
    is_active: bool
    email_verified: bool
    auth_provider: str

    class Config:
        from_attributes = True


@router.get("/me", response_model=UserInfoResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current user profile information"""
    return UserInfoResponse.from_orm(current_user)


@router.post("/upgrade-to-enterprise", response_model=TierUpgradeResponse)
async def upgrade_to_enterprise(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    DEV-ONLY ENDPOINT: Upgrade current user to enterprise tier

    This endpoint is for local development/testing only.
    Allows you to test enterprise features without upgrading in production.

    Usage:
    ```
    curl -X POST http://localhost:8000/api/v1/users/upgrade-to-enterprise \
      -H "Authorization: Bearer YOUR_JWT_TOKEN"
    ```
    """
    logger.warning(f"User {current_user.id} ({current_user.email}) upgraded to enterprise tier via dev endpoint")

    current_user.tier = "enterprise"
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    return TierUpgradeResponse(
        message="Successfully upgraded to enterprise tier",
        user_id=current_user.id,
        email=current_user.email,
        tier=current_user.tier,
        note="This is a development-only endpoint. Use /api/v1/billing for production upgrades."
    )


@router.post("/set-tier/{tier}", response_model=TierUpgradeResponse)
async def set_user_tier(
    tier: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    DEV-ONLY ENDPOINT: Set user tier to any value

    Valid tiers: "free", "pro", "enterprise"

    Usage:
    ```
    curl -X POST http://localhost:8000/api/v1/users/set-tier/pro \
      -H "Authorization: Bearer YOUR_JWT_TOKEN"
    ```
    """
    valid_tiers = ["free", "pro", "enterprise"]
    if tier not in valid_tiers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier. Must be one of: {', '.join(valid_tiers)}"
        )

    logger.warning(f"User {current_user.id} ({current_user.email}) set tier to {tier} via dev endpoint")

    current_user.tier = tier
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    return TierUpgradeResponse(
        message=f"Successfully set tier to {tier}",
        user_id=current_user.id,
        email=current_user.email,
        tier=current_user.tier,
        note="This is a development-only endpoint."
    )


@router.get("/tiers", tags=["users"])
async def get_available_tiers():
    """
    Get list of available tiers with their limits
    """
    return [
        {
            "name": "free",
            "price": 0,
            "max_duration": 30,
            "max_jobs_per_month": 3,
            "features": ["Basic voices", "30s max duration", "7-day file retention"]
        },
        {
            "name": "pro",
            "price": 19,
            "max_duration": 120,
            "max_jobs_per_month": 50,
            "features": ["All voices", "HD TTS", "120s max", "30-day retention", "Translation"]
        },
        {
            "name": "enterprise",
            "price": 99,
            "max_duration": 3600,
            "max_jobs_per_month": -1,
            "features": ["Unlimited duration", "Priority queue", "Custom branding", "90-day retention", "Dedicated support"]
        }
    ]
