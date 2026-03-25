from datetime import datetime

from pydantic import BaseModel


class TierInfo(BaseModel):
    name: str
    price: float
    limit: int  # -1 for unlimited
    features: list[str]


class UsageSummary(BaseModel):
    tier: str
    used: int
    limit: int  # -1 for unlimited
    remaining: int  # -1 for unlimited


class SubscriptionResponse(BaseModel):
    id: str
    tier: str
    status: str
    current_period_start: datetime | None
    current_period_end: datetime | None

    model_config = {"from_attributes": True}


class CheckoutRequest(BaseModel):
    tier: str


class CheckoutResponse(BaseModel):
    checkout_url: str
