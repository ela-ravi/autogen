import logging
from datetime import date, datetime, timezone

import stripe
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.permissions import TIER_QUOTAS
from app.models.subscription import Subscription
from app.models.usage import UsageRecord
from app.models.user import User

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

TIER_PRICES = {
    "pro": settings.STRIPE_PRICE_PRO,
    "enterprise": settings.STRIPE_PRICE_ENTERPRISE,
}


async def get_or_create_stripe_customer(db: AsyncSession, user: User) -> str:
    if user.stripe_customer_id:
        return user.stripe_customer_id

    customer = stripe.Customer.create(
        email=user.email,
        name=user.full_name,
        metadata={"user_id": user.id},
    )
    user.stripe_customer_id = customer.id
    await db.commit()
    return customer.id


async def create_checkout_session(
    db: AsyncSession, user: User, tier: str
) -> str:
    price_id = TIER_PRICES.get(tier)
    if not price_id:
        raise ValueError(f"Invalid tier: {tier}")

    customer_id = await get_or_create_stripe_customer(db, user)

    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url=f"{settings.CORS_ORIGINS[0]}/billing?success=true",
        cancel_url=f"{settings.CORS_ORIGINS[0]}/billing?cancelled=true",
        metadata={"user_id": user.id, "tier": tier},
    )
    return session.url


async def get_usage_summary(db: AsyncSession, user_id: str, tier: str) -> dict:
    if not settings.ENABLE_BILLING:
        return {"tier": tier, "used": 0, "limit": -1, "remaining": -1}

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
    used = result.scalar()
    limit = TIER_QUOTAS.get(tier, 3)
    remaining = -1 if limit == -1 else max(0, limit - used)

    return {"tier": tier, "used": used, "limit": limit, "remaining": remaining}


async def record_usage(db: AsyncSession, user_id: str, job_id: str):
    today = date.today()
    period_start = today.replace(day=1)

    record = UsageRecord(
        user_id=user_id,
        job_id=job_id,
        action="recap_created",
        period_start=period_start,
    )
    db.add(record)
    await db.commit()


def handle_webhook(payload: bytes, sig_header: str):
    """Process Stripe webhook events. Returns (event_type, data) or raises."""
    event = stripe.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
    )
    return event["type"], event["data"]["object"]
