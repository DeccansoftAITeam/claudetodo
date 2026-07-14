# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack

FastAPI + Pydantic, single-file app (`main.py`). v1 uses an in-memory dict keyed by todo id — there is no database, so state is lost on restart. See the root `CLAUDE.md` for the API contract and how this server is wired to the frontend.

## Commands

```bash
# Setup (first time)
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell (use source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt

# Run dev server with reload (serves on http://localhost:8000)
uvicorn main:app --reload

# Quick sanity check
curl http://localhost:8000/health     # -> {"status":"ok"}
```

There is no test runner or linter configured for the backend. Verify changes by running the server and hitting the endpoints (the frontend dev server proxies `/api` here).

## Architecture notes

- **All routes are under `/api`** except `/health`. Keep new endpoints on `/api` so the Vite proxy reaches them without config changes.
- **Validation is split:** Pydantic `Field(min_length=1, max_length=255)` on `TodoBase` rejects empty/over-length text with `422`, and every model uses `extra: "forbid"` so unknown fields are rejected. The whitespace-only case (`"   "`) passes Pydantic but is rejected explicitly in `create_todo` — keep that explicit check if you refactor.
- **Response models:** `list_todos`/`create_todo`/`update_todo` declare `response_model` so output is shaped by Pydantic; `delete_todo` returns `204` with no body. Unknown todo ids return `404`.
- **Store:** `_todos: dict[str, dict]` holds raw rows; `_to_todo` maps a row to the `Todo` response model. Newest-first ordering is derived at list time via `sorted(..., key=created_at, reverse=True)`, so insertion order in the dict does not matter.
- `created_at` is `datetime.now(timezone.utc).isoformat()` — a string, matching the `Todo.created_at: str` field. Don't store naive datetimes.