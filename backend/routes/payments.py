"""
payments.py — HTTP endpoints for starting payments and issuing refunds.

These call stripe_service (which talks to Stripe). The routes stay thin: look up the
order, ask the service to do the Stripe work, return the result.

Endpoints:
  POST /payments/checkout/{order_id} -> create a Stripe Checkout Session, return its URL
  POST /payments/checkout-cart       -> one session for a whole cart of products
  POST /payments/refund/{order_id}   -> refund that order's payment
  GET  /payments/success | /cancel   -> simple landing pages Stripe redirects back to
"""

import stripe
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend import config
from backend.database import get_db
from backend.models import Order, OrderStatus, Product
from backend.services import crud, stripe_service

router = APIRouter(prefix="/payments", tags=["payments"])


# Request shape for the cart checkout. The browser sends only product_id + quantity;
# the server looks the PRICE up itself (below), so a tampered-with price can't get
# through. Pydantic validates the JSON body into these typed objects.
class CartLine(BaseModel):
    product_id: int
    quantity: int


class CartCheckout(BaseModel):
    items: list[CartLine]


@router.post("/checkout/{order_id}")
def create_checkout(order_id: int, db: Session = Depends(get_db)):
    # Fail early with a clear message if keys aren't set, instead of a Stripe crash.
    if not config.stripe_is_configured():
        raise HTTPException(status_code=503, detail="Stripe is not configured (set STRIPE_SECRET_KEY in .env)")

    order = crud.get(db, Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    try:
        session = stripe_service.create_checkout_session(order)
    except stripe.StripeError as e:
        # Stripe rejected the request (bad key, bad data, etc.). Surface a clean 502.
        raise HTTPException(status_code=502, detail=f"Stripe error: {e.user_message or str(e)}")

    # Return the hosted payment page URL. The frontend (Phase 5) sends the user there.
    return {"checkout_url": session.url, "session_id": session.id}


@router.post("/checkout-cart")
def create_cart_checkout(payload: CartCheckout, db: Session = Depends(get_db)):
    """Turn a cart (list of product_id + quantity) into ONE Stripe Checkout Session."""
    if not config.stripe_is_configured():
        raise HTTPException(status_code=503, detail="Stripe is not configured (set STRIPE_SECRET_KEY in .env)")

    if not payload.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Build the line items from OUR database, not the browser's numbers.
    line_data = []
    for line in payload.items:
        if line.quantity < 1:
            raise HTTPException(status_code=400, detail="Quantity must be at least 1")
        product = crud.get(db, Product, line.product_id)
        if product is None:
            raise HTTPException(status_code=404, detail=f"Product {line.product_id} not found")
        line_data.append({"name": product.name, "amount": product.price, "quantity": line.quantity})

    try:
        session = stripe_service.create_cart_checkout_session(line_data)
    except stripe.StripeError as e:
        raise HTTPException(status_code=502, detail=f"Stripe error: {e.user_message or str(e)}")

    return {"checkout_url": session.url, "session_id": session.id}


@router.post("/refund/{order_id}")
def refund_order(order_id: int, db: Session = Depends(get_db)):
    if not config.stripe_is_configured():
        raise HTTPException(status_code=503, detail="Stripe is not configured (set STRIPE_SECRET_KEY in .env)")

    order = crud.get(db, Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    # We can only refund an order that actually has a Stripe payment recorded.
    if not order.stripe_payment_intent_id:
        raise HTTPException(status_code=400, detail="Order has no payment to refund")

    # Security/correctness guard: only PAID orders can be refunded. Blocks refunding
    # orders that are still pending, or already refunded (double-refund attempts).
    if order.status != OrderStatus.paid:
        raise HTTPException(
            status_code=400,
            detail=f"Only paid orders can be refunded (this order is '{order.status.value}')",
        )

    try:
        refund = stripe_service.create_refund(order.stripe_payment_intent_id)
    except stripe.StripeError as e:
        raise HTTPException(status_code=502, detail=f"Stripe error: {e.user_message or str(e)}")

    # Note: we DON'T mark the order refunded here. Stripe will send a charge.refunded
    # webhook, and the webhook handler updates the DB. That keeps the DB in sync with
    # Stripe as the single source of truth (more on this in webhooks.py).
    return {"refund_id": refund.id, "status": refund.status}


# --- Simple landing pages Stripe redirects to after the hosted checkout -----------
# In Phase 5 these become real frontend pages; for now they just confirm the round-trip.
@router.get("/success")
def checkout_success():
    return {"message": "Payment successful. You can close this tab."}


@router.get("/cancel")
def checkout_cancel():
    return {"message": "Payment canceled."}
