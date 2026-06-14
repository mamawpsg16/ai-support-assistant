"""
subscriptions.py — HTTP endpoints for subscriptions.
Like orders, it validates that the referenced customer exists before creating.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Customer, Subscription
from backend.schemas import SubscriptionCreate, SubscriptionRead, SubscriptionUpdate
from backend.services import crud

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


def _check_customer(db: Session, customer_id: int | None):
    """Raise 400 if a provided customer_id doesn't exist."""
    if customer_id is not None and crud.get(db, Customer, customer_id) is None:
        raise HTTPException(status_code=400, detail=f"Customer {customer_id} does not exist")


@router.post("/", response_model=SubscriptionRead, status_code=status.HTTP_201_CREATED)
def create_subscription(payload: SubscriptionCreate, db: Session = Depends(get_db)):
    _check_customer(db, payload.customer_id)
    return crud.create(db, Subscription, payload)


@router.get("/", response_model=list[SubscriptionRead])
def list_subscriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_all(db, Subscription, skip=skip, limit=limit)


@router.get("/{subscription_id}", response_model=SubscriptionRead)
def get_subscription(subscription_id: int, db: Session = Depends(get_db)):
    obj = crud.get(db, Subscription, subscription_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return obj


@router.patch("/{subscription_id}", response_model=SubscriptionRead)
def update_subscription(
    subscription_id: int,
    payload: SubscriptionUpdate,
    db: Session = Depends(get_db),
):
    obj = crud.get(db, Subscription, subscription_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    _check_customer(db, payload.customer_id)
    return crud.update(db, obj, payload)


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(subscription_id: int, db: Session = Depends(get_db)):
    obj = crud.get(db, Subscription, subscription_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    crud.delete(db, obj)
