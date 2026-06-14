"""
Subscription model = the `subscriptions` table.

A subscription is a recurring plan a customer is on (e.g. "Pro" billed monthly).
Same building blocks as Order: a foreign key to the customer, and an Enum for status.
"""

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.database import Base


class SubscriptionStatus(str, enum.Enum):
    """Allowed subscription states (mirrors how Stripe describes subscriptions)."""
    active = "active"          # paid and running
    canceled = "canceled"      # customer ended it
    past_due = "past_due"      # payment failed, awaiting retry


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)

    # Which customer this subscription belongs to.
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    # Human-readable plan name, e.g. "Basic", "Pro".
    plan_name = Column(String, nullable=False)

    status = Column(
        Enum(SubscriptionStatus),
        nullable=False,
        default=SubscriptionStatus.active,
    )

    # Stripe's id for this subscription. Filled in Phase 2; nullable for now.
    stripe_subscription_id = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # The other side of Customer.subscriptions.
    customer = relationship("Customer", back_populates="subscriptions")

    def __repr__(self):
        return f"<Subscription id={self.id} plan={self.plan_name!r} status={self.status}>"
