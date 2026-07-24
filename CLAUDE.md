# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

ClaudeTodo — a minimal single-user todo app. React (Vite) frontend talks to a Python FastAPI backend over REST. v1 has no auth, no database, and a single shared todo list. The full spec lives in [`PRD.md`](./PRD.md); see it before changing scope (e.g. adding persistence, filtering, or tags — all explicitly v1 non-goals).

## Layout

```
claudetodo/
├── PRD.md            # product spec — source of truth for behavior
├── render.yaml        # Render Blueprint — deploys backend + frontend as separate services
├── backend/          # FastAPI app, single main.py (see backend/CLAUDE.md)
└── frontend/         # React + Vite app (see frontend/CLAUDE.md)
```

Each subfolder has its own `CLAUDE.md` with stack-specific commands and conventions. Read the one for the side you're editing.

## How the two halves connect

- **API contract:** all todos routes are under `/api` (`GET /api/todos`, `POST /api/todos`, `PATCH /api/todos/{id}`, `DELETE /api/todos/{id}`). `GET /health` is the liveness probe.
- **Dev wiring:** the Vite dev server (`:5173`) proxies `/api` and `/health` to the FastAPI server (`:8000`) — see `frontend/vite.config.js`. So during development the frontend calls relative paths like `/api/todos` and they reach the backend automatically. **Both servers must be running** for the app to work locally.
- **Todo shape:** `{ id: string (UUID), text: string, completed: boolean, created_at: ISO8601 string, category: string }`. The backend generates `id` and `created_at`; the client sends `text` + optional `category` (POST) or `completed` (PATCH). Text is 1–255 chars, trimmed.
- **Category:** a fixed enum — `General`, `Work`, `Personal`, `Shopping` — defined once in the backend `Category` enum and mirrored by the frontend `CATEGORIES` constant (keep them in sync). Optional on POST, defaults to `General`; an unknown value is a `422`. Set at creation and not editable (no PATCH support). Filtering by category is **client-side only** — `GET /api/todos` always returns every todo; there is no `?category=` param.
- **Ordering:** `GET /api/todos` returns newest-first (sorted by `created_at` desc). The frontend also prepends newly created todos, so don't re-sort on the client.

## Working in this repo

- Keep changes inside the boundary they belong to — backend data/validation logic in `backend/`, UI/state in `frontend/`. The API contract above is the seam; change both sides together if you change it.
- There is no test suite in v1 and no CI. Verify by running both servers and exercising the create/complete/delete/reload flow against the acceptance criteria in PRD.md §10.
- `backend/.venv/`, `frontend/node_modules/`, `frontend/dist/`, and `__pycache__/` are build artifacts — never edit or commit them.

## Deployment

Backend and frontend deploy as two separate Render services, defined in `render.yaml` (a Render Blueprint — "New +" → "Blueprint" in the Render dashboard, pointed at this repo).

- **Backend** (`claudetodo-backend`): Python web service, `uvicorn main:app --host 0.0.0.0 --port $PORT`. CORS is wide open (`allow_origins=["*"]`) in `main.py` since there's no auth/cookies to protect — this is what lets the frontend call it from a different Render host.
- **Frontend** (`claudetodo-frontend`): static site built with `npm run build`. Since it's on a different host than the backend, relative `/api/...` fetches won't reach it — `App.jsx` prefixes requests with `API_BASE`, built from the `VITE_API_URL` env var (empty in dev, so the Vite proxy still works locally). The blueprint wires `VITE_API_URL` to the backend service's hostname automatically via `fromService`.
- **Free-tier caveat:** Render's free web services have an ephemeral filesystem — `backend/todos.db` gets wiped on every redeploy and likely on spin-down/spin-up after 15 min of inactivity. Fine for a demo; don't rely on it for real data without a paid persistent disk.