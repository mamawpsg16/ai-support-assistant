"""
config.py — load settings/secrets from the environment (.env file).

Why this file exists:
  Secret keys (Stripe, later AI) must NOT be hardcoded in the source — they'd leak the
  moment you share or commit the code. They live in a .env file (which .gitignore keeps
  out of git), and we read them here in ONE place. Everything else imports from here.

How it works:
  - load_dotenv() reads .env and loads each KEY=VALUE line into the environment.
  - os.getenv("NAME", default) then reads a value (or a default if it's missing).

To set real values: copy .env.example to .env and paste your Stripe TEST keys.
"""

import os

from dotenv import load_dotenv

# Read .env (if present) into environment variables. Safe to call even if the file is
# missing — values just come back as the defaults and the app still imports fine.
load_dotenv()


# --- Stripe (Phase 2) ------------------------------------------------------------
# Secret key: identifies your Stripe account, server-side only. Test keys start with
# "sk_test_". NEVER send this to the browser/frontend.
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")

# Webhook signing secret: used to verify incoming webhooks really came from Stripe.
# The Stripe CLI prints this (starts "whsec_") when you run `stripe listen` — later step.
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# After paying on Stripe's hosted page, Stripe redirects the customer back to the SPA
# (the Vue storefront on :5173), not to a JSON endpoint. These match routes in the
# Vue router (CheckoutSuccess / CheckoutCancel views).
CHECKOUT_SUCCESS_URL = os.getenv(
    "CHECKOUT_SUCCESS_URL", "http://localhost:5173/checkout/success"
)
CHECKOUT_CANCEL_URL = os.getenv(
    "CHECKOUT_CANCEL_URL", "http://localhost:5173/checkout/cancel"
)


def stripe_is_configured() -> bool:
    """True only if a Stripe secret key is set. Routes use this to return a clear
    'Stripe not configured' message instead of a confusing crash when keys are absent."""
    return bool(STRIPE_SECRET_KEY)


# --- RAG (Phase 3) ---------------------------------------------------------------
# Folder holding the markdown knowledge base (return policy, shipping, FAQ...). These
# are the documents RAG searches over.
KNOWLEDGE_DIR = os.getenv("KNOWLEDGE_DIR", "backend/knowledge")

# Folder where Chroma persists the vector store to disk (like support.db, but for
# embeddings). Git-ignored and rebuildable from the markdown at any time.
CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")


# --- AI chat (Phase 4) -----------------------------------------------------------
# Groq serves open models (Llama) over an OpenAI-compatible API — free + fast, and it
# supports tool calling, which the assistant needs. Key starts "gsk_".
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Which Groq model to chat with. llama-3.3-70b-versatile is a strong tool-calling model.
# Overridable via env so you can swap models without touching code.
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def groq_is_configured() -> bool:
    """True only if a Groq key is set. The chat route uses this to return a clear
    'AI not configured' message instead of crashing when the key is absent."""
    return bool(GROQ_API_KEY)
