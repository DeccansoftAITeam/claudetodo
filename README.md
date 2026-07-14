# ClaudeTodo

A lightweight todo application with a React (Vite) frontend and a Python FastAPI backend.

## Features (v1)

- Create todos
- Mark todos as complete
- Delete todos

See [`PRD.md`](./PRD.md) for the full product requirements document.

## Project Structure

```
claudetodo/
├── PRD.md            # Product requirements document
├── README.md         # This file
├── backend/          # FastAPI API
│   ├── main.py
│   └── requirements.txt
└── frontend/         # React + Vite app
    └── src/App.jsx
```

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv

# Activate the virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (cmd):
.venv\Scripts\activate.bat
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

The API runs at `http://localhost:8000`. Health check: `GET /health`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server runs at `http://localhost:5173`.