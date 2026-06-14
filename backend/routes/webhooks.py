"""
webhooks.py — the endpoint Stripe calls to tell us things happened.

A webhook is Stripe POSTing to our server when an event occurs ("payment completed",
"refund issued", "subscription canceled"). This is how our DB learns about things that
happened on Stripe's hosted pages, which our own code never saw directly.

Flow:
  customer pays on Stripe -> Stripe POSTs an event here -> we verify it's really Stripe
  -> we read the event type -> we update our database.

SECURITY (critical): anyone could POST fake "payment done" events. So Stripe SIGNS each
request, and we verify that signature with STRIPE_WEBHOOK_SECRET before trusting it.
Verification needs the RAW request body (exact bytes), so we read request.body()
ourselves instead of letting FastAPI parse the JSON.

--------------------------------------------------------------------------------------
WHAT AN EVENT LOOKS LIKE (checkout.session.completed), trimmed:

  {
    "id": "evt_1Abc...",
    "type": "checkout.session.completed",     <- event["type"]
    "data": {
      "object": {                             <- event["data"]["object"]  (the session)
        "id": "cs_test_a1b2c3...",
        "payment_intent": "pi_3XyZ...",       <- saved on the order, used for refunds
        "amount_total": 2500,                 <- cents
        "currency": "usd",
        "payment_status": "paid",
        "metadata": { "order_id": "3" }       <- OUR data, echoed back to us
      }
    }
  }

For "charge.refunded", data.object is a CHARGE instead, e.g.:
  { "id": "ch_...", "payment_intent": "pi_3XyZ...", "amount_refunded": 2500, ... }

For "customer.subscription.*", data.object is a SUBSCRIPTION:
  { "id": "sub_...", "status": "active" | "past_due" | "canceled", ... }
--------------------------------------------------------------------------------------
"""

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from backend import config
from backend.database import get_db
from backend.models import Order, OrderStatus, Subscription, SubscriptionStatus

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
    # Stripe puts the signature in the "Stripe-Signature" HTTP header. Header(None)
    # reads that header into this param (FastAPI maps stripe_signature -> Stripe-Signature).
    stripe_signature: str = Header(None),
):
    # 1. RAW body bytes — required for signature verification (parsing would change them).
    payload = await request.body()

    # 2. Verify the signature and parse the event in one step.
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=stripe_signature,
            secret=config.STRIPE_WEBHOOK_SECRET,
        )
    except (ValueError, stripe.SignatureVerificationError):
        # Bad payload or signature didn't match our secret -> reject it.
        raise HTTPException(status_code=400, detail="Invalid Stripe signature")

    # 3. React based on the event type. `event["data"]["object"]` is the thing the
    #    event is about (a checkout session, a charge, a subscription, ...).
    event_type = event["type"]
    obj = event["data"]["object"]

    if event_type == "checkout.session.completed":
        _handle_checkout_completed(db, obj)
    elif event_type == "charge.refunded":
        _handle_charge_refunded(db, obj)
    elif event_type in (
        "customer.subscription.created",
        "customer.subscription.updated",
        "customer.subscription.deleted",
    ):
        _handle_subscription_event(db, event_type, obj)
    # Any other event types: we just acknowledge them (return 200) and do nothing.

    # Always return 200 quickly so Stripe knows we received it (else it retries).
    return {"received": True}


# --- Handlers (one small function per event, kept private with a leading _) --------

def _handle_checkout_completed(db: Session, session_obj):
    """Payment finished -> mark the order paid and save its PaymentIntent id.

    session_obj is the "session" dict shown in the header comment. We read order_id
    out of the metadata we attached when creating the session (stripe_service.py)."""
    order_id = session_obj.get("metadata", {}).get("order_id")
    if not order_id:
        return  # no order linked -> nothing to do

    order = db.query(Order).filter(Order.id == int(order_id)).first()
    if order is None:
        return

    order.status = OrderStatus.paid
    # The PaymentIntent id ("pi_...") is what we later use to issue refunds.
    order.stripe_payment_intent_id = session_obj.get("payment_intent")
    db.commit()


def _handle_charge_refunded(db: Session, charge_obj):
    """A charge was refunded -> mark the matching order refunded.
    charge_obj is a "charge" dict; we match it to an order via payment_intent."""
    payment_intent_id = charge_obj.get("payment_intent")
    if not payment_intent_id:
        return

    order = (
        db.query(Order)
        .filter(Order.stripe_payment_intent_id == payment_intent_id)
        .first()
    )
    if order is None:
        return

    order.status = OrderStatus.refunded
    db.commit()


def _handle_subscription_event(db: Session, event_type: str, sub_obj):
    """Keep our Subscription rows in sync with Stripe's subscription state.
    sub_obj is a "subscription" dict with an id and a status string."""
    stripe_sub_id = sub_obj.get("id")
    if not stripe_sub_id:
        return

    subscription = (
        db.query(Subscription)
        .filter(Subscription.stripe_subscription_id == stripe_sub_id)
        .first()
    )
    if subscription is None:
        # We only sync subscriptions we already track. (Creating brand-new ones from
        # webhooks would need customer mapping — out of scope for this phase.)
        return

    if event_type == "customer.subscription.deleted":
        subscription.status = SubscriptionStatus.canceled
    else:
        # Map Stripe's status string ("active"/"past_due"/...) onto our enum if valid.
        stripe_status = sub_obj.get("status")
        try:
            subscription.status = SubscriptionStatus(stripe_status)
        except ValueError:
            pass  # unknown status -> leave it unchanged

    db.commit()
