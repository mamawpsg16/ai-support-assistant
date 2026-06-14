# AI-Powered Customer Support Assistant (E-commerce)

A learning project built in phases: a FastAPI backend + a Vue 3 storefront, with Stripe
payments (test mode), and — later — RAG + an AI chat assistant.

**Architecture: decoupled (separate frontend/backend) in a monorepo.** Two independent
apps in one repo, talking over HTTP/JSON:

```
new-project/
├── backend/     FastAPI API only            → http://localhost:8000   (see backend/README.md)
├── frontend/    Vue 3 + Vite + Bootstrap SPA → http://localhost:5173   (see frontend/README.md)
├── docker-compose.yml   run both with one command
├── SECURITY.md          security posture + deferred auth work
└── CLAUDE.md            notes for AI coding sessions
```

## Quick start — Docker (one command, Windows or Ubuntu)

Prereqs: Docker Desktop (Windows) or Docker Engine + compose (Ubuntu).

```bash
cp .env.example .env          # then add your Stripe TEST keys to .env
docker compose up --build
```
- Backend → http://localhost:8000 (docs at `/docs`), **auto-seeds** sample data on first run.
- Frontend → http://localhost:5173
- Both **hot-reload** when you edit files.
- For paid/refund flows, run the Stripe CLI on the host:
  `stripe listen --forward-to http://localhost:8000/webhooks/stripe`

Stop: `docker compose down` (data persists in a volume). Reset data: `docker compose down -v`.

## Quick start — native (no Docker)

```bash
# Backend (from repo root)
python -m venv .venv && .venv\Scripts\activate     # macOS/Linux: source .venv/bin/activate
pip install -r backend/requirements.txt
python -m backend.seed
uvicorn backend.main:app --reload                  # http://localhost:8000

# Frontend (separate terminal)
cd frontend && npm install && npm run dev          # http://localhost:5173
```

See **backend/README.md** and **frontend/README.md** for details (endpoints, structure,
Stripe testing, etc.).

## Tech stack

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite, Pydantic v2, Stripe (test mode).
- **Frontend:** Vue 3 (Composition API), Vite, Bootstrap 5, vue-router, axios,
  vue-multiselect, Vuelidate.
- **Tooling:** Docker + docker-compose, Stripe CLI for webhooks.

## Status

- [x] **Phase 1 — Foundation** (models, CRUD, support lookups, seed, /health)
- [x] **Phase 2 — Stripe** (checkout, webhooks, refunds — test mode)
- [x] **Storefront frontend** (Vue SPA exercising all APIs) — pulled forward from Phase 5
- [x] **Dockerized** (one-command run, hot reload, auto-seed)
- [ ] **Security/auth pass** (deferred — see `SECURITY.md`; no auth yet)
- [ ] **Phase 3 — RAG** (FAQ/policy docs in Chroma)
- [ ] **Phase 4 — AI chat** (Claude/Groq tool calling) + chat widget in the SPA

> Heads-up: there is **no authentication yet** — every endpoint is open. Fine for local
> dev; see `SECURITY.md` before deploying anywhere real.
 