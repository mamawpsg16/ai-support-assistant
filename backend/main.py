"""
main.py — the application entry point.

This is the file the server runs: `uvicorn backend.main:app` (backend.main = this file,
app = the FastAPI object below). Its jobs:
  1. create the FastAPI app,
  2. make sure the database tables exist,
  3. plug in every router (customers, products, orders, subscriptions, support),
  4. expose a /health check.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, engine
# Importing the models package RUNS backend/models/__init__.py, which imports all 4 model
# classes. Defining those classes is what registers their tables on Base.metadata —
# so this import must happen BEFORE create_all() below, or no tables get built.
from backend import models  # noqa: F401  (imported for its side effect of registering models)
from backend.routes import chat, customers, orders, payments, products, search, subscriptions, support, webhooks

# Create the database tables if they don't already exist (safe to run every startup).
# Fine for a learning project; real apps use migrations (e.g. Alembic) instead.
Base.metadata.create_all(bind=engine)

# The FastAPI application object. title/version show up on the auto-generated /docs page.
app = FastAPI(
    title="AI Customer Support Assistant",
    version="0.1.0",
    description="Phase 1 — foundation API (models, CRUD, support lookups).",
)

# --- CORS -------------------------------------------------------------------------
# The Vue SPA runs on a DIFFERENT origin (http://localhost:5173) than this API
# (http://127.0.0.1:8000). Browsers block cross-origin requests by default (a security
# feature). CORS = the server saying "I allow calls from these origins."
#
# Origins are read from the CORS_ORIGINS env var (comma-separated) so the allowed port
# can change with the frontend's port (Docker sets this). Defaults cover the dev server.
_cors_origins = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _cors_origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],   # allow GET, POST, PATCH, DELETE, OPTIONS...
    allow_headers=["*"],   # allow Content-Type and any other request headers
)

# Register each router. Now all their paths (e.g. /customers, /support/...) are live.
app.include_router(customers.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(subscriptions.router)
app.include_router(support.router)
app.include_router(payments.router)    # Phase 2: Stripe checkout + refund
app.include_router(webhooks.router)    # Phase 2: Stripe webhook receiver
app.include_router(search.router)      # Phase 3: RAG knowledge-base search
app.include_router(chat.router)        # Phase 4: AI chat assistant (Groq + tools)


# GET /health -> a tiny endpoint to confirm the API is up.
# Load balancers / monitoring tools ping this to check the service is alive.
@app.get("/health", tags=["meta"])
def health_check():
    return {"status": "ok"}


# GET / -> friendly root that points you to the interactive docs.
@app.get("/", tags=["meta"])
def root():
    return {
        "message": "AI Customer Support Assistant API (Phase 1)",
        "docs": "/docs",
        "health": "/health",
    }
