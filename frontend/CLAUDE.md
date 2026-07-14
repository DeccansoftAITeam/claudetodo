# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack

React 19 + Vite 8, plain JSX (no TypeScript despite `@types/*` devDeps). Linting via Oxlint. No state library, no HTTP library, no UI framework — `useState` + `fetch`. See the root `CLAUDE.md` for the API contract and how this app is wired to the backend.

## Commands

```bash
npm install        # first time
npm run dev        # dev server on http://localhost:5173 (proxies /api -> :8000, so run the backend too)
npm run build      # production build to dist/
npm run preview    # serve the production build locally
npm run lint       # oxlint (config in .oxlintrc.json)
```

There is no test runner. Verify changes by running `npm run dev` plus the backend, and exercising the create/complete/delete/reload flow.

## Architecture notes

- **Everything lives in `src/App.jsx`** — the `api()` fetch wrapper, validation, and all state/handlers. `main.jsx` only mounts `<App />`. Styling is `index.css` (base) + `App.css` (component styles using BEM-ish class names like `todo--done`).
- **`api(path, { method, body })`** is the single HTTP entry point: sets `Content-Type` only when there's a body, returns `null` for `204`, and throws an `Error` whose `.message` is the server's `detail` (or `${status} ${statusText}` if no JSON). Call it with **relative** paths (`/api/todos`) so the Vite proxy handles routing in dev and same-origin serving in production.
- **Validation before network:** `validate(text)` checks empty/whitespace and `MAX_TEXT` (255, matching the backend) **before** any fetch — empty/whitespace submissions never hit the network (PRD acceptance #4). Keep `MAX_TEXT` in sync with the backend's `max_length=255` if either changes.
- **Optimistic updates with revert:** `toggleTodo` and `deleteTodo` mutate local state immediately, then reconcile on success or roll back on failure (setting `error`). Preserve this pattern for any new mutating actions.
- **`useEffect` load is cancellation-aware** — the `alive` flag prevents setting state after unmount. Keep that guard if you touch the initial load.
- **Oxlint rules** (`.oxlintrc.json`): `react/rules-of-hooks` is `error`, `react/only-export-components` is `warn` with `allowConstantExport`. The `api` helper and `MAX_TEXT` are the constant exports this allows.