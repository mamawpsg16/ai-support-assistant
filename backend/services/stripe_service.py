"""
stripe_service.py — all direct calls to the Stripe SDK live here.

Keeping Stripe code in one service (not scattered across routes) means the routes stay
simple and there's a single place to change if Stripe's API changes. Think of it like
crud.py, but for Stripe instead of the database.

Two key Stripe facts baked in below:
  1. MONEY IS IN CENTS. Stripe wants the smallest currency unit, so $25.00 -> 2500.
  2. METADATA. We attach our own order_id to the Stripe session. When Stripe later
     sends a webhook, it carries that order_id back, so we know which Order to update.
"""

import stripe

from backend import config
from backend.models import Order

# Tell the Stripe SDK which account to act as. This sets it once for the whole app.
# Empty until you put STRIPE_SECRET_KEY in .env; calls just fail clearly if so.
stripe.api_key = config.STRIPE_SECRET_KEY


def dollars_to_cents(amount: float) -> int:
    """Convert a dollar amount (25.0) to Stripe's integer cents (2500).
    round() avoids floating-point surprises like 2499.999 -> we want a clean int."""
    return round(amount * 100)


def create_checkout_session(order: Order):
    """
    Ask Stripe to create a hosted Checkout Session for one order.

    Returns the Stripe session object. The important field on it is `.url` — the
    hosted payment page we send the customer to.

    We build the line item from the order's product (name + price), set mode="payment"
    (a one-time charge, not a subscription), and stash order.id in metadata so the
    webhook can match the payment back to this order.
    """
    product = order.product  # works via the relationship() we set on the Order model

    session = stripe.checkout.Session.create(
        mode="payment",  # one-time payment (use "subscription" for recurring plans)
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": product.name},
                    "unit_amount": dollars_to_cents(order.total),  # cents!
                },
                "quantity": 1,
            }
        ],
        # Stripe sends the customer to one of these after paying / cancelling.
        success_url=config.CHECKOUT_SUCCESS_URL,
        cancel_url=config.CHECKOUT_CANCEL_URL,
        # Our own data, echoed back to us in the webhook event.
        metadata={"order_id": str(order.id)},
    )
    return session


def create_cart_checkout_session(items: list[dict]):
    """
    Create ONE hosted Checkout Session for a whole cart (several products at once).

    `items` is a list of {"name", "amount" (dollars), "quantity"} dicts that the route
    builds AFTER looking each price up in our own DB — so the amount charged never comes
    from the browser (a client could otherwise tamper with prices).

    Unlike create_checkout_session() above, this does NOT create Order rows, so there's
    no order_id metadata and the webhook leaves it alone. It's a straight "pay for these
    line items" session. (Tracking cart purchases as Orders is a later step — see the
    redesign plan.)
    """
    line_items = [
        {
            "price_data": {
                "currency": "usd",
                "product_data": {"name": it["name"]},
                "unit_amount": dollars_to_cents(it["amount"]),  # cents!
            },
            "quantity": it["quantity"],
        }
        for it in items
    ]

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=line_items,
        success_url=config.CHECKOUT_SUCCESS_URL,
        cancel_url=config.CHECKOUT_CANCEL_URL,
    )
    return session


def create_refund(payment_intent_id: str):
    """
    Refund a payment by its PaymentIntent id (the "pi_..." string saved on the order).

    Stripe processes the refund AND fires a `charge.refunded` webhook, which our
    webhook handler uses to mark the order refunded in our DB.
    """
    refund = stripe.Refund.create(payment_intent=payment_intent_id)
    return refund
