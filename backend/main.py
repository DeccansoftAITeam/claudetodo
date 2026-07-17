import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

DB_PATH = Path(__file__).parent / "todos.db"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the table on startup. WAL mode keeps writes crash-safe.
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            completed INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()
    yield


app = FastAPI(title="ClaudeTodo API", version="1.0", lifespan=lifespan)


def _get_conn() -> sqlite3.Connection:
    # check_same_thread=False: uvicorn may serve requests across threads.
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


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


def _to_todo(row: sqlite3.Row) -> Todo:
    return Todo(
        id=row["id"],
        text=row["text"],
        completed=bool(row["completed"]),
        created_at=row["created_at"],
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/todos", response_model=list[Todo])
def list_todos():
    # Newest first: sort by created_at descending.
    conn = _get_conn()
    rows = conn.execute(
        "SELECT id, text, completed, created_at FROM todos ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [_to_todo(r) for r in rows]


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
        "completed": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    conn = _get_conn()
    conn.execute(
        "INSERT INTO todos (id, text, completed, created_at) VALUES (?, ?, ?, ?)",
        (row["id"], row["text"], row["completed"], row["created_at"]),
    )
    conn.commit()
    conn.close()
    return _to_todo(row)


@app.patch("/api/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: str, payload: TodoUpdate):
    conn = _get_conn()
    cur = conn.execute(
        "UPDATE todos SET completed = ? WHERE id = ?",
        (1 if payload.completed else 0, todo_id),
    )
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="todo not found")
    row = conn.execute(
        "SELECT id, text, completed, created_at FROM todos WHERE id = ?", (todo_id,)
    ).fetchone()
    conn.commit()
    conn.close()
    return _to_todo(row)


@app.delete("/api/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: str):
    conn = _get_conn()
    cur = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="todo not found")
    conn.commit()
    conn.close()
    return None