# Product Requirements Document — ClaudeTodo

**Version:** 1.0
**Date:** 2026-07-13
**Status:** Draft

## 1. Overview

ClaudeTodo is a lightweight task-management web application that lets users capture, track, and complete everyday tasks. It is intentionally minimal — a clean, single-page experience focused on the core todo lifecycle: create, complete, and delete.

## 2. Goals & Non-Goals

**Goals**
- Provide a fast, distraction-free todo list.
- Deliver a reliable create / complete / delete flow with instant feedback.
- Establish a clean client–server split that is easy to extend later.

**Non-goals (v1)**
- User accounts, authentication, or multi-device sync.
- Due dates, reminders, tags, priorities, or subtasks.
- Offline support or collaboration.

## 3. Users

A single assumed user on a single device. No login. Todos are scoped to one shared list in v1.

## 4. User Stories

- As a user, I can add a todo by typing text and submitting it.
- As a user, I can mark a todo as complete (and un-complete it).
- As a user, I can delete a todo.
- As a user, I can see all my todos and their current state at a glance.

## 5. Functional Requirements

| ID | Requirement |
|----|-------------|
| F1 | Create a todo with non-empty text (trim and validate). |
| F2 | List all todos, newest first, each with its completed state. |
| F3 | Toggle a todo's `completed` flag. |
| F4 | Delete a todo. |
| F5 | Persist todos across page reloads via the backend. |
| F6 | Reject empty/whitespace-only todo text with a client-side error. |

## 6. Data Model

**Todo**

| Field | Type | Notes |
|-------|------|-------|
| `id` | string (UUID) | Server-generated. |
| `text` | string | 1–255 chars, trimmed. |
| `completed` | boolean | Defaults to `false`. |
| `created_at` | ISO 8601 datetime | Server-generated. |

## 7. API

REST over JSON. Base path: `/api`.

| Method | Path | Body | Response |
|--------|------|------|----------|
| `GET` | `/todos` | — | `200` `Todo[]` |
| `POST` | `/todos` | `{ text }` | `201` `Todo` |
| `PATCH` | `/todos/{id}` | `{ completed }` | `200` `Todo` |
| `DELETE` | `/todos/{id}` | — | `204` |

Validation: `POST` rejects empty/over-length text with `422`. Unknown id returns `404`.

## 8. Technology

- **Frontend:** React + Vite (TypeScript). `fetch` for HTTP. Minimal styling; no UI framework required.
- **Backend:** Python FastAPI. Pydantic models for request/response validation. In-memory list store for v1 (no database).
- **Dev proxy:** Vite dev server proxies `/api` to FastAPI (default `http://localhost:8000`).

## 9. UX Guidelines

- Input box always visible at the top; Enter submits.
- Each todo row: checkbox, text, delete button.
- Completed todos render with strikethrough and muted styling.
- Optimistic UI updates on toggle/delete; reconcile on server response.

## 10. Acceptance Criteria

1. Adding a todo creates a persisted entry visible after reload.
2. Toggling a todo updates its completed state and persists across reloads.
3. Deleting a todo removes it from the list and from the store.
4. Empty submission is blocked with an inline error and no network call.
5. App loads with the current todo list from the backend.

## 11. Future Considerations

Persistence (SQLite/Postgres), due dates, tags, filtering (all/active/completed), and optional auth.