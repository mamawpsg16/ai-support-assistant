"""
Order model = the `orders` table.

An order links a customer to a product they bought, plus its status and total.
This file introduces two new concepts:

  1. FOREIGN KEY: a column that points at another table's id. `customer_id` holds
     the id of the customer who placed the order. This is how relational databases
     connect rows across tables.

  2. ENUM (enumeration): a fixed set of allowed values. An order's status can only
     be one of pending/paid/shipped/delivered/refunded — nothing else. We define a
     Python Enum so typos like "shiped" become impossible in our code.
"""

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.database import Base


class OrderStatus(str, enum.Enum):
    """
    The allowed order statuses.

    Subclassing `str` (so it's `(str, enum.Enum)`) means each member also behaves
    like a plain string — e.g. OrderStatus.paid == "paid" is True. That makes it
    easy to store/compare and to send over the web as JSON text.
    """
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    delivered = "delivered"
    refunded = "refunded"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    # FOREIGN KEYS -> point at the id columns of other tables.
    # "customers.id" is table_name.column_name. nullable=False = every order must
    # belong to a customer and a product.
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Status column backed by the Enum above. The DB stores the text ("paid"), but
    # our Python code is forced to use a valid OrderStatus value.
    status = Column(
        Enum(OrderStatus),
        nullable=False,
        default=OrderStatus.pending,
    )

    # The amount charged for this order.
    total = Column(Float, nullable=False)

    # Stripe's id for the payment attempt. Filled in Phase 2; nullable for now.
    stripe_payment_intent_id = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships: the other side of Customer.orders and Product.orders.
    # These let us write order.customer and order.product to get the full objects.
    customer = relationship("Customer", back_populates="orders")
    product = relationship("Product", back_populates="orders")

    def __repr__(self):
        return f"<Order id={self.id} status={self.status} total={self.total}>"
