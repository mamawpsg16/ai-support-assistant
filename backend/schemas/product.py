"""
Product schemas — API shape of a product. Same 3-schema pattern as customer.
"""

from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    description: str | None = None   # optional text
    price: float
    stripe_price_id: str | None = None   # optional now; used in Phase 2


# INPUT for creating a product.
class ProductCreate(ProductBase):
    pass


# INPUT for editing: all fields optional.
class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    stripe_price_id: str | None = None


# OUTPUT: adds the DB-generated id.
class ProductRead(ProductBase):
    id: int

    model_config = {"from_attributes": True}
