"""
Customer schemas — the API "shape" of a customer (Pydantic models).

Mental model (Laravel comparison):
  - CustomerCreate / CustomerUpdate  ~ a Laravel Form Request (validate INPUT)
  - CustomerRead                     ~ a Laravel API Resource (shape OUTPUT)
  - the SQLAlchemy model             ~ the Eloquent model (the DB table)

Pydantic validates by TYPE: `name: str` already means "required string", and FastAPI
auto-returns a 422 error if the client sends bad data.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr


# Shared parent: fields common to create + read, so we don't retype them (DRY).
class CustomerBase(BaseModel):
    name: str
    email: EmailStr  # validates it looks like a real email


# INPUT for creating: client sends name + email only (DB makes id/created_at).
class CustomerCreate(CustomerBase):
    pass


# INPUT for editing: every field optional so the client can change just one.
class CustomerUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None


# OUTPUT: what the API sends back. Adds the DB-generated id + created_at.
class CustomerRead(CustomerBase):
    id: int
    created_at: datetime

    # Lets Pydantic read fields straight off a SQLAlchemy row object (.id, .name...).
    model_config = {"from_attributes": True}
