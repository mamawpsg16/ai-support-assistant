"""
Subscription schemas — API shape of a subscription. Same pattern as order:
status uses the SubscriptionStatus enum so only valid states are accepted.
"""

from datetime import datetime

from pydantic import BaseModel

from backend.models.subscription import SubscriptionStatus


class SubscriptionBase(BaseModel):
    customer_id: int
    plan_name: str
    status: SubscriptionStatus | None = None   # optional on input
    stripe_subscription_id: str | None = None  # filled in Phase 2


# INPUT for creating.
class SubscriptionCreate(SubscriptionBase):
    pass


# INPUT for editing: all optional (e.g. flip status active -> canceled).
class SubscriptionUpdate(BaseModel):
    customer_id: int | None = None
    plan_name: str | None = None
    status: SubscriptionStatus | None = None
    stripe_subscription_id: str | None = None


# OUTPUT: + DB-generated id/created_at.
class SubscriptionRead(SubscriptionBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
