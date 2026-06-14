"""
Product model = the `products` table.

This is the simplest table: things a customer can buy. It already includes a
`stripe_price_id` column even though we don't use Stripe until Phase 2 — adding the
column now means we won't have to change the table later.
"""

from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import relationship

from backend.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    # A longer text description. nullable=True (the default) -> optional.
    description = Column(String, nullable=True)

    # Price in dollars. Float stores decimals like 19.99.
    # (In real money-handling apps people often use Integer cents or Numeric to avoid
    #  floating-point rounding; Float is fine for this learning project.)
    price = Column(Float, nullable=False)

    # Stripe identifies each purchasable price with an id like "price_123abc".
    # We store it here so Phase 2 can create checkout sessions. Nullable for now.
    stripe_price_id = Column(String, nullable=True)

    # One product can appear in many orders. Mirror of Order.product.
    orders = relationship("Order", back_populates="product")

    def __repr__(self):
        return f"<Product id={self.id} name={self.name!r} price={self.price}>"
