# Task Tracker

A learning-focused Task Tracker application built with a FastAPI backend and
a plain HTML/CSS/JS Kanban frontend. Supports full CRUD on tasks, status
transitions, due dates with overdue detection, and search/filtering.

## Architecture

- **Backend:** FastAPI + Pydantic v2, with JSON file storage (`data/tasks.json`)
- **Frontend:** Single-file HTML/CSS/JS Kanban board (`frontend/index.html`)
- **Tests:** pytest, using FastAPI's `TestClient`

See `docs/midcourse/mini-adr.md` and the original ADR-001 for design
decisions.

## Project Structure

task-tracker/
├── app/
│ ├── main.py # FastAPI app and routes
│ ├── models.py # Pydantic models
│ ├── storage.py # In-memory + JSON file persistence
│ └── business_rules.py # Status-transition validation
├── data/
│ └── tasks.json # Task data (JSON file storage)
├── frontend/
│ └── index.html # Kanban board UI
├── tests/
│ ├── conftest.py
│ ├── test_health.py
│ └── test_tasks.py
├── docs/
│ └── midcourse/ # Mid-course project documentation
├── requirements.txt
├── .env.example
└── .gitignore
## Setup

### 1. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

## Running the Backend

With the virtual environment active:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

- Health check: `http://localhost:8000/health`
- Interactive API docs (Swagger): `http://localhost:8000/docs`

## Running the Frontend

The frontend is a static HTML file and needs to be served separately from
the backend. In a **second terminal** (with the backend still running in
the first):

```bash
cd frontend
python -m http.server 8080
```

Then open your browser to:

http://localhost:8080

The frontend expects the backend to be running on `http://localhost:8000`
(configured via CORS in `app/main.py`).

## Running Tests

With the virtual environment active, from the project root:

```bash
python -m pytest -v
```

This runs the full test suite (health check + all task CRUD, validation,
business rule, due date, and search tests).

## API Overview

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/tasks` | Create a task |
| GET | `/tasks` | List tasks (supports `status`, `priority`, `overdue`, `search` query params) |
| GET | `/tasks/{id}` | Get a single task |
| PATCH | `/tasks/{id}` | Update a task (partial) |
| DELETE | `/tasks/{id}` | Delete a task |

## Notes

- Task storage is JSON-file-backed (`data/tasks.json`) — no database required.
- Duplicate tasks (same title, description, status, priority, assignee) are
  rejected with `409 Conflict`.
- Status transitions follow a fixed set of allowed moves (see
  `app/business_rules.py`); invalid transitions return `422`.
- A task is considered "overdue" if its `due_date` is in the past and its
  status is not `Done`.
  