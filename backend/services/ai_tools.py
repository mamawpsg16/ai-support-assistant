"""
ai_tools.py — the "tools" the AI assistant can call (Phase 4).

Three things live here, and it's worth understanding the split:

  1. TOOL_SCHEMAS  — JSON descriptions we SEND to the model. The model reads these to
                     decide which tool to call and with what arguments. It never sees our
                     Python; only these descriptions. So good descriptions = good tool use.

  2. tool_*()      — the REAL functions that actually run (query the DB, call Stripe, RAG).
                     Each returns a plain dict (JSON-serializable) — never a SQLAlchemy
                     object — because the result gets sent back to the model as text.

  3. dispatch()    — glue. Given a tool name + arguments (from the model), it finds the
                     matching tool_* function, runs it, and returns its dict. Errors are
                     caught and returned as {"error": ...} so one bad call never crashes
                     the chat — the model sees the error and can recover.

Flow reminder: model says "call get_order_status(order_id=42)" -> dispatch() runs
tool_get_order_status(db, order_id=42) -> result dict goes back to the model.
"""

from sqlalchemy.orm import Session

from backend.models import Customer, Order, OrderStatus
from backend.services import rag, stripe_service
from backend import config


# =============================================================================
# 1. TOOL SCHEMAS — what the model sees (OpenAI/Groq "function" format).
# =============================================================================
# Each entry: name (must match a function below), a clear description (the model relies
# on this to pick the right tool), and a JSON Schema for the arguments.
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_faq",
            "description": (
                "Search the store's help/policy knowledge base (shipping, returns, "
                "refunds, subscriptions, FAQ). Use for general 'how does X work' questions "
                "that are NOT about a specific customer's order or account."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's question, in natural language.",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": (
                "Look up the current status, total, and date of ONE order by its numeric "
                "order id. Use when the user asks about a specific order."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer",
                        "description": "The order's numeric id.",
                    }
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_subscription",
            "description": (
                "List the subscription plan(s) and status for a customer, by numeric "
                "customer id. Use for billing/plan/cancel questions about an account."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "The customer's numeric id.",
                    }
                },
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "process_refund",
            "description": (
                "Refund a paid order by its numeric order id. Only works on orders that are "
                "PAID and have a recorded payment. Use ONLY after the user clearly asks for "
                "a refund and you have confirmed which order."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer",
                        "description": "The numeric id of the paid order to refund.",
                    }
                },
                "required": ["order_id"],
            },
        },
    },
]


# =============================================================================
# 2. TOOL IMPLEMENTATIONS — the real work. Each returns a JSON-serializable dict.
# =============================================================================
def tool_search_faq(query: str) -> dict:
    """RAG lookup (Phase 3). Returns the top knowledge-base chunks for the model to read."""
    hits = rag.search_faq(query, k=3)
    # Strip the distance / trim to what the model needs as context.
    return {
        "results": [
            {"source": h["source"], "heading": h["heading"], "text": h["text"]}
            for h in hits
        ]
    }


def tool_get_order_status(db: Session, order_id: int) -> dict:
    """Look up one order. Returns an error dict (not an exception) if not found."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        return {"error": f"Order {order_id} not found"}
    return {
        "order_id": order.id,
        "status": order.status.value if order.status else None,
        "total": order.total,
        "created_at": order.created_at.isoformat() if order.created_at else None,
    }


def tool_get_customer_subscription(db: Session, customer_id: int) -> dict:
    """List a customer's subscriptions. Empty list if they have none."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer is None:
        return {"error": f"Customer {customer_id} not found"}
    return {
        "customer_id": customer.id,
        "subscriptions": [
            {
                "id": s.id,
                "plan_name": s.plan_name,
                "status": s.status.value if s.status else None,
            }
            for s in customer.subscriptions
        ],
    }


def tool_process_refund(db: Session, order_id: int) -> dict:
    """Refund a paid order via Stripe.

    SECURITY NOTE (learning project): letting an AI trigger refunds is powerful and risky.
    We're in Stripe TEST mode with no real money, and there's no auth yet (see SECURITY.md),
    so this is safe to demo. A real app MUST require human confirmation + verify the user
    actually owns this order before refunding. The same paid-only / has-payment guards from
    the /payments route are repeated here so the AI can't refund something invalid.
    """
    if not config.stripe_is_configured():
        return {"error": "Stripe is not configured; cannot process refunds."}

    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        return {"error": f"Order {order_id} not found"}
    if not order.stripe_payment_intent_id:
        return {"error": f"Order {order_id} has no payment to refund."}
    if order.status != OrderStatus.paid:
        return {"error": f"Only paid orders can be refunded (order {order_id} is '{order.status.value}')."}

    try:
        refund = stripe_service.create_refund(order.stripe_payment_intent_id)
    except Exception as exc:  # Stripe error etc. — report it back to the model, don't crash.
        return {"error": f"Stripe refund failed: {exc}"}

    # The DB is updated by the charge.refunded webhook, not here (same as the route).
    return {"refund_id": refund.id, "status": refund.status}


# =============================================================================
# 3. DISPATCH — turn a model's tool call (name + args) into a real result.
# =============================================================================
# Tools that need DB access take `db` as their first argument; search_faq does not.
_NEEDS_DB = {"get_order_status", "get_customer_subscription", "process_refund"}
_IMPLEMENTATIONS = {
    "search_faq": tool_search_faq,
    "get_order_status": tool_get_order_status,
    "get_customer_subscription": tool_get_customer_subscription,
    "process_refund": tool_process_refund,
}


def dispatch(name: str, arguments: dict, db: Session) -> dict:
    """Run the named tool with the given arguments. Always returns a dict.

    Any unknown tool or any exception becomes an {"error": ...} dict, so the chat loop
    can hand it back to the model and the conversation keeps going instead of 500-ing.
    """
    func = _IMPLEMENTATIONS.get(name)
    if func is None:
        return {"error": f"Unknown tool: {name}"}
    try:
        if name in _NEEDS_DB:
            return func(db, **arguments)
        return func(**arguments)
    except TypeError as exc:
        # Model sent wrong/missing arguments for this tool.
        return {"error": f"Bad arguments for {name}: {exc}"}
    except Exception as exc:
        return {"error": f"{name} failed: {exc}"}
