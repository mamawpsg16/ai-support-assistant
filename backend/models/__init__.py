"""
This file makes `backend/models/` a package AND re-exports every model in one place.

Why import them all here? Two reasons:
  1. Convenience: other code can do `from backend.models import Customer, Order`.
  2. Registration: a model only registers its table on `Base.metadata` once its
     module is imported. By importing all four here, anything that imports the
     `models` package guarantees all tables are known before create_all() runs.
"""

from backend.models.customer import Customer
from backend.models.product import Product
from backend.models.order import Order, OrderStatus
from backend.models.subscription import Subscription, SubscriptionStatus

# __all__ lists the names exported when someone does `from backend.models import *`.
__all__ = [
    "Customer",
    "Product",
    "Order",
    "OrderStatus",
    "Subscription",
    "SubscriptionStatus",
]
