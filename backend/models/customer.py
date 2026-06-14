"""
Customer model = the `customers` table in the database.

A "model" is a Python class that SQLAlchemy maps to a database table:
  - the class       -> a table
  - each attribute  -> a column
  - each instance   -> a row
This style is called an ORM (Object-Relational Mapper): you work with Python
objects, and SQLAlchemy writes the SQL for you.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from backend.database import Base


class Customer(Base):
    # __tablename__ is the actual table name created in SQLite.
    __tablename__ = "customers"

    # primary_key=True  -> unique row identifier.
    # autoincrement     -> SQLite assigns 1, 2, 3, ... automatically. We never set it.
    # index=True        -> builds an index so lookups by id are fast.
    id = Column(Integer, primary_key=True, index=True)

    # A person's name. nullable=False means this column is required.
    name = Column(String, nullable=False)

    # unique=True -> the database rejects two customers with the same email.
    email = Column(String, unique=True, nullable=False, index=True)

    # When the row was created. `default=datetime.utcnow` tells SQLAlchemy to fill
    # this in automatically at insert time. (We pass the function itself, no par_
    # entheses, so it's called fresh for each new row.)
    created_at = Column(DateTime, default=datetime.utcnow)

    # --- Relationships (not real columns; convenience links to other tables) ------
    # A customer can have many orders and many subscriptions.
    # `relationship` lets us write `customer.orders` in Python and get a list of
    # Order objects, instead of writing a manual SQL JOIN.
    #   back_populates ties the two sides together (Order.customer <-> Customer.orders).
    #   cascade="all, delete-orphan" -> deleting a customer also deletes their orders/subs.
    orders = relationship(
        "Order",
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    subscriptions = relationship(
        "Subscription",
        back_populates="customer",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        # __repr__ controls how the object prints — handy for debugging/seed output.
        return f"<Customer id={self.id} name={self.name!r}>"
