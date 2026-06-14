"""
support.py — read-only "lookup" endpoints used by customer support.

These answer the common questions a support agent asks:
  - What's the status of order X?
  - What has customer Y ordered?
  - What subscription is customer Y on?

Why separate from the CRUD routers? Because in Phase 4 the AI assistant will call
these exact lookups as "tools" (get_order_status, etc.). Keeping them grouped here
makes that wiring clean. They only READ data — no create/update/delete.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Customer, Order
from backend.schemas import OrderRead, SubscriptionRead

router = APIRouter(prefix="/support", tags=["support"])


# GET /support/order/{order_id}/status
# Returns a small summary of one order's status. (Becomes the get_order_status tool.)
@router.get("/order/{order_id}/status")
def order_status(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    # Return a plain dict -> FastAPI turns it straight into JSON.
    return {
        "order_id": order.id,
        "status": order.status,
        "total": order.total,
        "created_at": order.created_at,
    }


# GET /support/customer/{customer_id}/orders
# All orders placed by one customer. response_model shapes each as an OrderRead.
@router.get("/customer/{customer_id}/orders", response_model=list[OrderRead])
def customer_orders(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    # customer.orders works because of the relationship() we set up on the model.
    return customer.orders


# GET /support/customer/{customer_id}/subscription
# A customer's subscription(s). Returns a list (a customer may have 0, 1, or more).
@router.get("/customer/{customer_id}/subscription", response_model=list[SubscriptionRead])
def customer_subscription(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    return customer.subscriptions
