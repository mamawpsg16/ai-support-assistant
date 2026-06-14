# CLAUDE.md — Project Memory

Guidance for future Claude Code sessions working on this repo.

## What this project is

An **AI-powered customer support assistant for e-commerce**, built in phases as a
learning project. The user is learning Python, AI integration, Stripe, RAG, and Vue, so
**explain concepts as you go and keep teaching comments in the code. Go one file/step
at a time and make sure the user understands before moving on.**

## Working rule (important)

Build **one phase at a time, then STOP for user review** before starting the next.
Do not jump ahead unless asked. The user asks lots of "why" questions — answer them
before writing the file.

## Architecture

**Decoupled (separated frontend/backend) in a monorepo.** Not a monolith — the server
does NOT render HTML.

```
new-project/        ← one repo
├── backend/        ← FastAPI API only            :8000   (was named app/, renamed)
├── frontend/       ← Vue 3 + Vite SPA            :5173
├── seed.py         ← standalone DB seed script (run: python seed.py)
└── support.db      ← SQLite file (git-ignored, auto-created)
```
The SPA calls the API over HTTP/JSON; that's why the API needs **CORS** (allows
localhost:5173). Run the backend with `uvicorn backend.main:app --reload`.

## Status

- **Phase 1 — Foundation (DONE):** FastAPI + SQLAlchemy + SQLite; models, schemas,
  CRUD, support lookups, seed, /health.
- **Phase 2 — Stripe (DONE):** checkout sessions, webhooks (signature-verified),
  refunds, test mode. Verified end-to-end with Stripe CLI.
- **Storefront frontend (DONE, pulled forward from Phase 5):** Vue 3 + Vite + Bootstrap
  5 SPA exercising all APIs (store/checkout, orders+refund, subscriptions, manage CRUD).
- **Security pass (DEFERRED — next):** NO auth yet; every endpoint is open. See
  `SECURITY.md`. Add login + route guards + ownership checks before any real deploy.
- **Phase 3 — RAG (pending):** FAQ/policy markdown embedded in Chroma + retrieval.
- **Phase 4 — AI chat (pending):** chat endpoint with tool calling (get_order_status,
  get_customer_subscription, process_refund, search_faq). Provider not locked —
  Anthropic Claude vs Groq (free). Both keys live in `.env`. Wire chat widget into SPA.

## Locked decisions

- **SQLite** for now (SQLAlchemy keeps it swappable to Postgres = connection-string change).
- **Sync** SQLAlchemy (not async). **Integer auto-increment** PKs. **Pydantic v2**.
- Status fields = TEXT in DB, guarded by Python `Enum`.
- Backend deps via **requirements.txt + venv**. Frontend via **npm** (in `frontend/`).
- Frontend: **Composition API + `<script setup>`**, **template-first** block order,
  **DRY** (composables `useAsync`/`useCrud`, generic `Picker`, `api/` resource factory),
  **vue-multiselect** for dropdowns, **Vuelidate** for form validation, **layered**
  folder structure with the API client in its own `src/api/` folder.

## Backend folder convention (keep phases additive)

```
backend/
  main.py        # FastAPI app + CORS + router registration + /health
  config.py      # loads .env secrets (Stripe keys, AI keys)
  database.py    # engine, SessionLocal, Base, get_db()
  models/        # SQLAlchemy ORM models = DB tables
  schemas/       # Pydantic models = API request/response contracts
  routes/        # one router per resource (+ support.py, payments.py, webhooks.py)
  services/      # business logic (crud.py, stripe_service.py; rag.py later)
```
Each later phase ADDS files (e.g. `services/rag.py`, `routes/chat.py`).

## Common commands

```bash
# --- One command (Docker) — works on Windows or Ubuntu ---
docker compose up --build               # backend :8000 + frontend :5173, auto-seeds DB
# (copy .env.example to .env with Stripe test keys first)

# --- Or run natively ---
# Backend (run from repo root)
python -m venv .venv
.venv\Scripts\activate                  # Windows
pip install -r backend/requirements.txt
python -m backend.seed                  # (re)create + populate support.db
uvicorn backend.main:app --reload       # http://127.0.0.1:8000 ; docs at /docs
# Stripe webhooks (Phase 2): stripe listen --forward-to http://127.0.0.1:8000/webhooks/stripe

# Frontend
cd frontend
npm install
npm run dev                             # http://localhost:5173
```

Layout note: `requirements.txt` and `seed.py` now live in `backend/`. Run `seed` as a
module (`python -m backend.seed`) from the repo root. `DATABASE_URL` env var overrides the
DB path (Docker points it at a volume); defaults to `sqlite:///./support.db`.

## Gotchas

- On Windows, editing .py files with PowerShell `Set-Content` can corrupt em-dashes —
  use the Write/Edit tools or `[IO.File]::WriteAllText(path, text, UTF8(no BOM))`.
- Stripe Link popup on checkout is Stripe's saved-card login, not our code — use a
  throwaway email + test card `4242 4242 4242 4242` to skip it.
- `stripe listen` prints a fresh `whsec_` each run; if webhooks fail with "Invalid
  signature", update `STRIPE_WEBHOOK_SECRET` in `.env` and restart the backend.
```
