# Security Notes

Tracking what's secured and what's intentionally deferred. This is a **local learning
project using Stripe TEST keys** — these notes describe the gap between "fine for local"
and "safe for production."

## Already in place ✅

- **Secrets in `.env`, git-ignored.** Stripe keys never committed (`.gitignore` covers
  `.env` at any depth + `.env.*`).
- **Stripe secret key is server-side only.** The Vue SPA never receives `sk_test_`; it
  only calls our API, and our API calls Stripe.
- **Webhook signature verification.** `/webhooks/stripe` rejects events whose signature
  doesn't match `STRIPE_WEBHOOK_SECRET` (`backend/routes/webhooks.py`).
- **CORS is a specific whitelist** (`http://localhost:5173`), not `*` (`backend/main.py`).
- **SQL injection safe.** All DB access goes through SQLAlchemy (parameterized).
- **Input validation.** Pydantic schemas reject malformed requests (422).
- **Refund guard.** Only `paid` orders can be refunded — blocks double-refunds and
  refunding unpaid orders (`backend/routes/payments.py`).

## Deferred — do in the dedicated auth pass ⚠️

> **#1 gap: there is NO authentication/authorization yet.** Every endpoint is open.
> Anyone who can reach the API can delete customers, manage products, and refund/checkout
> any order. Acceptable for local dev; must be fixed before any real deployment.

Planned auth pass:
- User accounts + login (hashed passwords, e.g. `passlib[bcrypt]`).
- Tokens (JWT or session) issued on login.
- Route guards: protect all **write** endpoints (POST/PATCH/DELETE) and **payments**
  (`/payments/checkout`, `/payments/refund`).
- Ownership checks: a customer can only see/act on their own orders & subscriptions
  (the `/support/customer/{id}/...` lookups currently trust the id in the URL).

## TODO — rate limiting (not yet implemented)

No rate limiting today. When added (e.g. `slowapi` / a reverse proxy), prioritize:
- **Login** endpoint (once it exists) — blunt brute-force attempts.
- **`/payments/checkout`** and **`/payments/refund`** — prevent abuse / runaway Stripe calls.
- **Webhook** endpoint — Stripe already signs requests, but a cap limits flooding.

## Operational reminders

- Rotate the Stripe key if it ever lands in a commit, a screenshot, or a chat.
- Use **live** keys only behind HTTPS + auth, never in `.env.example` or the frontend.
- `support.db` is git-ignored; don't commit a DB with real data.
