import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.billing import (
    CheckoutRequest,
    CheckoutResponse,
    SubscriptionResponse,
    TierInfo,
    UsageSummary,
)
from app.services import billing_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/billing", tags=["billing"])

TIERS = [
    TierInfo(
        name="free", price=0, limit=3,
        features=["Basic voices", "30s max duration", "7-day file retention"],
    ),
    TierInfo(
        name="pro", price=19, limit=50,
        features=["All voices", "HD TTS", "120s max", "30-day retention", "Translation"],
    ),
    TierInfo(
        name="enterprise", price=99, limit=-1,
        features=["Priority queue", "Custom branding", "90-day retention", "Dedicated support"],
    ),
]


@router.get("/tiers", response_model=list[TierInfo])
async def get_tiers():
    return TIERS


@router.get("/usage", response_model=UsageSummary)
async def get_usage(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    summary = await billing_service.get_usage_summary(
        db, current_user.id, current_user.tier
    )
    return summary


@router.get("/subscription", response_model=SubscriptionResponse | None)
async def get_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    return result.scalar_one_or_none()


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    body: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.tier not in ("pro", "enterprise"):
        raise HTTPException(status_code=400, detail="Invalid tier")

    try:
        url = await billing_service.create_checkout_session(
            db, current_user, body.tier
        )
        return CheckoutResponse(checkout_url=url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")

    try:
        event_type, data = billing_service.handle_webhook(payload, sig)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if event_type == "checkout.session.completed":
        user_id = data.get("metadata", {}).get("user_id")
        tier = data.get("metadata", {}).get("tier")
        if user_id and tier:
            from app.services.user_service import get_by_id
            user = await get_by_id(db, user_id)
            if user:
                user.tier = tier
                # Create or update subscription
                result = await db.execute(
                    select(Subscription).where(Subscription.user_id == user_id)
                )
                sub = result.scalar_one_or_none()
                if sub:
                    sub.tier = tier
                    sub.stripe_subscription_id = data.get("subscription", "")
                    sub.status = "active"
                else:
                    sub = Subscription(
                        user_id=user_id,
                        tier=tier,
                        stripe_subscription_id=data.get("subscription", ""),
                        status="active",
                    )
                    db.add(sub)
                await db.commit()

    elif event_type == "customer.subscription.deleted":
        sub_id = data.get("id")
        result = await db.execute(
            select(Subscription).where(Subscription.stripe_subscription_id == sub_id)
        )
        sub = result.scalar_one_or_none()
        if sub:
            sub.status = "cancelled"
            sub.tier = "free"
            from app.services.user_service import get_by_id
            user = await get_by_id(db, sub.user_id)
            if user:
                user.tier = "free"
            await db.commit()

    return {"status": "ok"}
