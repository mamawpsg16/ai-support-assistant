# Backend — FastAPI API

The API for the AI Customer Support Assistant. Python + FastAPI + SQLAlchemy + SQLite,
with Stripe (test mode). **API only** — the UI lives in `../frontend` (a separate Vue app).

## Run with Docker (easiest)

From the repo root: `docker compose up --build` — see the root `README.md`. This runs the
API (with auto-seed) and the frontend together. The rest of this file is the native setup.

## Setup & run natively (Windows / PowerShell)

```powershell
# from the project root (one level up from this folder)
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt

python -m backend.seed               # create + populate support.db with sample data
uvicorn backend.main:app --reload    # http://127.0.0.1:8000  (docs at /docs)
```
> macOS/Linux: `source .venv/bin/activate`. Run all commands from the **project root** so
> the `backend` package is importable. `seed` runs as a module (`python -m backend.seed`).
> Set `DATABASE_URL` to override the DB location (defaults to `sqlite:///./support.db`).

## Environment (.env at project root)

Copy `.env.example` to `.env` and fill in (Stripe test keys):
```
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...      # printed by `stripe listen` (see below)
```

## Folder layout

```
backend/
  main.py        # app + CORS + router registration + /health
  config.py      # loads .env secrets
  database.py    # engine, SessionLocal, Base, get_db()
  models/        # SQLAlchemy ORM models (DB tables)
  schemas/       # Pydantic request/response models
  routes/        # customers, products, orders, subscriptions, support, payments, webhooks
  services/      # crud.py, stripe_service.py
```

## Endpoints

### Meta
| Method | Path | |
|---|---|---|
| GET | `/health` | `{"status":"ok"}` |

### CRUD (customers / products / orders / subscriptions)
| Method | Path |
|---|---|
| POST | `/{resource}/` |
| GET | `/{resource}/` (supports `?skip=&limit=`) |
| GET | `/{resource}/{id}` |
| PATCH | `/{resource}/{id}` |
| DELETE | `/{resource}/{id}` |

### Support lookups (read-only; reused by the AI tools in Phase 4)
| Method | Path |
|---|---|
| GET | `/support/order/{order_id}/status` |
| GET | `/support/customer/{customer_id}/orders` |
| GET | `/support/customer/{customer_id}/subscription` |

### Payments (Stripe, test mode)
| Method | Path | |
|---|---|---|
| POST | `/payments/checkout/{order_id}` | returns a Stripe `checkout_url` |
| POST | `/payments/refund/{order_id}` | only `paid` orders can be refunded |
| POST | `/webhooks/stripe` | Stripe → us (signature-verified) |

## Stripe webhooks (local testing)

```bash
# install the Stripe CLI, then:
stripe listen --forward-to http://127.0.0.1:8000/webhooks/stripe
#   ^ copy the printed whsec_... into .env as STRIPE_WEBHOOK_SECRET, restart uvicorn

# fire a test event:
stripe trigger checkout.session.completed --add "checkout_session:metadata.order_id=2"
```
Webhooks are how orders flip to **paid** / **refunded** — Stripe is the source of truth;
the API only changes the DB when Stripe confirms via a webhook.

## Notes

- **No auth yet** — every endpoint is open. See `../SECURITY.md`. Deferred to a dedicated
  auth pass.
- SQLite file `support.db` is created at the project root; re-run `python seed.py` to reset.
- Pending phases: 3 (RAG), 4 (AI chat with tool calling).
