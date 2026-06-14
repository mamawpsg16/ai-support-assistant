"""
Order schemas — API shape of an order.

New vs customer/product: the status field uses the OrderStatus enum from the model,
so the API also only accepts the five valid statuses.
"""

from datetime import datetime

from pydantic import BaseModel

# Reuse the SAME enum the model uses, so DB + API agree on valid statuses.
from backend.models.order import OrderStatus


class OrderBase(BaseModel):
    customer_id: int          # which customer (foreign key value)
    product_id: int           # which product
    total: float
    # status is optional on input; if omitted the DB default (pending) is used.
    status: OrderStatus | None = None
    stripe_payment_intent_id: str | None = None  # filled in Phase 2


# INPUT for creating an order.
class OrderCreate(OrderBase):
    pass


# INPUT for editing: all optional. Common real use: change status pending -> shipped.
class OrderUpdate(BaseModel):
    customer_id: int | None = None
    product_id: int | None = None
    total: float | None = None
    status: OrderStatus | None = None
    stripe_payment_intent_id: str | None = None


# OUTPUT: brings in OrderBase's fields (inheritance) + adds DB-generated id/created_at.
class OrderRead(OrderBase):
    id: int
    created_at: datetime

    # Lets Pydantic read fields off the SQLAlchemy row object when we `return order`.
    model_config = {"from_attributes": True}
