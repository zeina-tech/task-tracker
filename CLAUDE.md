# CLAUDE.md

# CLAUDE.md

## Tech stack

- Python 3.11
- FastAPI
- Pydantic v2
- Uvicorn
- pytest
- httpx
- Vanilla JavaScript frontend in `frontend/index.html`

## Run command

Use this exact command to run the backend:

```text
uvicorn app.main:app --reload --port 8000
```

The API is served at `http://localhost:8000`. The static frontend can be
served separately from `frontend/` on port 8080.

## Test command

Use this exact command to run the test suite:

```text
pytest -v
```

## Architecture summary

- Backend:
	- `app/main.py` — FastAPI application, routes, and CORS configuration.
	- `app/models.py` — Pydantic request/response models and task status/priority enums.
	- `app/storage.py` — In-memory task operations with JSON persistence in `data/tasks.json`.
	- `app/business_rules.py` — Task status-transition rules.
- Frontend:
	- `frontend/index.html` — Single-file HTML/CSS/vanilla JavaScript Kanban interface.
- Tests:
	- `tests/test_health.py` — Health endpoint tests.
	- `tests/test_tasks.py` — Task CRUD, validation, filtering, due-date, and business-rule tests.
	- `tests/conftest.py` — Test fixtures and storage reset behavior.
- Task rules live in `app/business_rules.py`; task status values are defined in
	`app/models.py`.

## Business rules

Task status values are:

- `ToDo`
- `InProgress`
- `Done`

Allowed status transitions are:

- `ToDo` -> `InProgress`
- `InProgress` -> `Done`
- `Done` -> `InProgress` (reopening a completed task)

Same-status updates and all transitions not listed above are rejected with
HTTP 422. The authoritative transition table is
`app.business_rules.VALID_TRANSITIONS`.

## UI states and CORS

The frontend supports these board states:

- Loading tasks
- Ready with tasks
- Empty results when no tasks match the filters
- Error loading or updating tasks, with retry support for load errors

The task modal supports create and edit modes, client-side title validation,
server-side field/form errors, and cancellation. The Kanban board supports
drag-and-drop status updates and search, status, priority, and overdue filters.

CORS is configured in `app/main.py` for:

- `http://localhost:8080`
- `http://127.0.0.1:8080`

Credentials, all methods, and all headers are allowed by the current
configuration.

## Do-not rules

- Do not add authentication or authorization.
- Do not add a database.
- Do not add deployment steps or deployment infrastructure.
- Do not make major UI changes without asking first.

@README.md