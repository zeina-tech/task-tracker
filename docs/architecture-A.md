# Task Tracker Architecture

## What the app does

Task Tracker is a small Kanban-style web app for creating, viewing, updating, filtering, and deleting tasks. A vanilla JavaScript frontend calls a FastAPI REST API, which persists task data to a local JSON file.

## Data model

**Task** is the sole domain entity. It has `id` (UUID), `title`, `description`, `status`, `priority`, `assignee`, `due_date`, `is_overdue`, `created_at`, and `updated_at`.

`status` is one of `ToDo`, `InProgress`, or `Done`; `priority` is `Low`, `Medium`, or `High`. `is_overdue` is computed when a task is created or updated: it is true only when `due_date` is before the current UTC date and the task is not `Done`.

## Request flow: creating a task

1. The user submits the create-task modal in `frontend/index.html`.
2. Client-side code trims and requires a title, then sends `POST /tasks` as JSON.
3. FastAPI binds and validates the request against `TaskCreate`.
4. `storage.add_task()` rejects an existing task with the same title, description, status, priority, and assignee.
5. Storage generates a UUID and UTC timestamps, computes `is_overdue`, adds the task to in-memory state, and rewrites `data/tasks.json`.
6. The API returns the created `TaskResponse` with HTTP 201; the frontend closes the modal and reloads the board. Duplicates return HTTP 409.

## Key files

- `app/main.py` — FastAPI app, CORS setup, and health/task routes.
- `app/models.py` — Pydantic request/response models and status/priority enums.
- `app/storage.py` — In-memory task collection plus JSON loading, persistence, and filtering.
- `app/business_rules.py` — Permitted task-status transition validation.
- `frontend/index.html` — Single-file Kanban UI, form handling, API calls, filters, and drag/drop.
- `data/tasks.json` — JSON-backed task persistence file.
- `tests/test_tasks.py` — API behavior tests for CRUD, validation, filtering, overdue logic, and persistence.
- `tests/conftest.py` — Test client and isolated storage reset fixtures.
- `README.md` — Setup, run, API, and high-level architecture documentation.

## Conventions

Pydantic rejects unknown request fields and validates enum/date values; titles are trimmed, required, and limited to 200 characters. Storage is process-local in memory but persisted by rewriting one JSON file after each mutation. API errors use FastAPI HTTP exceptions: validation errors are 422, duplicate creation is 409, and missing tasks are 404. The browser frontend communicates directly with `http://localhost:8000` using `fetch`; CORS permits the documented local frontend origins.

## Not visible or assumptions

No authentication, database, deployment configuration, or multi-process/concurrent-write strategy is visible in the inspected implementation. This document assumes the frontend is served from the documented local port 8080 and that JSON-file persistence is intended for this learning-focused application rather than production use.
