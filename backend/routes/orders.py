"""
orders.py — HTTP endpoints for orders.

New vs customers/products: an order references a customer AND a product by id.
Before creating one we VALIDATE that those ids actually exist, otherwise we'd save an
order pointing at a customer/product that isn't there. We return a clear 400 if not.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Customer, Order, Product
from backend.schemas import OrderCreate, OrderRead, OrderUpdate
from backend.services import crud

router = APIRouter(prefix="/orders", tags=["orders"])


def _check_refs(db: Session, customer_id: int | None, product_id: int | None):
    """
    Helper: make sure the referenced customer/product exist.
    Only checks ids that were provided (so it works for both create and update).
    Raises a 400 error if an id points to nothing.
    """
    if customer_id is not None and crud.get(db, Customer, customer_id) is None:
        raise HTTPException(status_code=400, detail=f"Customer {customer_id} does not exist")
    if product_id is not None and crud.get(db, Product, product_id) is None:
        raise HTTPException(status_code=400, detail=f"Product {product_id} does not exist")


@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    # Validate foreign keys before inserting.
    _check_refs(db, payload.customer_id, payload.product_id)
    return crud.create(db, Order, payload)


@router.get("/", response_model=list[OrderRead])
def list_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_all(db, Order, skip=skip, limit=limit)


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)):
    obj = crud.get(db, Order, order_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return obj


@router.patch("/{order_id}", response_model=OrderRead)
def update_order(order_id: int, payload: OrderUpdate, db: Session = Depends(get_db)):
    obj = crud.get(db, Order, order_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Order not found")
    # If the update changes customer/product, validate the new ids too.
    _check_refs(db, payload.customer_id, payload.product_id)
    return crud.update(db, obj, payload)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    obj = crud.get(db, Order, order_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Order not found")
    crud.delete(db, obj)
