from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="ClaudeTodo API", version="1.0")

# In-memory store for v1 (no database). Keyed by todo id.
# Newest-first ordering is derived when listing, so insertion order is fine.
_todos: dict[str, dict] = {}


class TodoBase(BaseModel):
    text: str = Field(min_length=1, max_length=255)

    model_config = {"extra": "forbid"}


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    completed: bool

    model_config = {"extra": "forbid"}


class Todo(BaseModel):
    id: str
    text: str
    completed: bool
    created_at: str


def _to_todo(row: dict) -> Todo:
    return Todo(
        id=row["id"],
        text=row["text"],
        completed=row["completed"],
        created_at=row["created_at"],
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/todos", response_model=list[Todo])
def list_todos():
    # Newest first: sort by created_at descending.
    ordered = sorted(_todos.values(), key=lambda r: r["created_at"], reverse=True)
    return [_to_todo(r) for r in ordered]


@app.post("/api/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate):
    text = payload.text.strip()
    # Pydantic guards empty/over-length, but a whitespace-only string is not
    # empty so reject it explicitly here.
    if not text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="text must not be empty",
        )
    row = {
        "id": str(uuid4()),
        "text": text,
        "completed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _todos[row["id"]] = row
    return _to_todo(row)


@app.patch("/api/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: str, payload: TodoUpdate):
    row = _todos.get(todo_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="todo not found")
    row["completed"] = payload.completed
    return _to_todo(row)


@app.delete("/api/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: str):
    if todo_id not in _todos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="todo not found")
    del _todos[todo_id]
    return None