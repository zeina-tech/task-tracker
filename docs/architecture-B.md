# Task Tracker Architecture

## What the app does

Task Tracker is a FastAPI-based REST application with a vanilla JavaScript Kanban interface for creating, viewing, filtering, updating, and deleting tasks across `ToDo`, `InProgress`, and `Done` statuses.

## Data model

**Task** is the primary entity. Create requests support `title`, `description`, `status`, `priority`, `assignee`, and `due_date`. Responses also contain generated `id`, computed `is_overdue`, and UTC `created_at` / `updated_at` timestamps. Status values are `ToDo`, `InProgress`, and `Done`; priorities are `Low`, `Medium`, and `High`.

## Request flow: create a task

1. The frontend modal validates that the title is not blank, then sends `POST /tasks` as JSON to `http://localhost:8000`.
2. FastAPI parses the request as `TaskCreate`; Pydantic rejects unknown fields, invalid enum/date values, blank titles, and titles over 200 characters.
3. `storage.add_task` checks for an existing task with the same title, description, status, priority, and assignee. Duplicates return `409`.
4. For a valid task, storage generates a UUID and UTC timestamps, derives `is_overdue`, retains it in memory, and writes all tasks to `data/tasks.json`.
5. The API returns `201` with `TaskResponse`; the frontend closes the modal and reloads the task list.

## Key files

- `app/main.py` — FastAPI app, CORS configuration, and task/health routes.
- `app/models.py` — Pydantic request/response models, task enums, and title validation.
- `app/storage.py` — In-memory task collection backed by `data/tasks.json`.
- `app/business_rules.py` — Allowed status-transition validation.
- `frontend/index.html` — Static Kanban UI, form handling, API calls, filtering, and drag/drop.
- `data/tasks.json` — Persisted task records.
- `tests/test_tasks.py` — API tests for CRUD, validation, persistence, filters, and overdue behavior.
- `tests/conftest.py` — Test client and storage-reset fixtures.
- `README.md` — Setup, run, API, and architecture overview.

## Conventions

- **Validation:** Pydantic v2 models forbid extra fields; titles are trimmed, required, and capped at 200 characters. Enums constrain statuses and priorities.
- **Storage:** Tasks load into an in-memory dictionary at application import and are persisted as JSON after creates, updates, and deletes. No database is used.
- **Error handling:** Framework/model validation returns `422`; duplicate creates return `409`; missing task IDs return `404`; invalid status transitions return `422`.
- **Frontend/backend interaction:** The static frontend uses `fetch` with JSON payloads against the API on port 8000; CORS permits localhost port 8080. After a successful create or edit, it reloads tasks. UI errors are displayed for failed requests.

## Not visible or assumptions

- Authentication, authorization, multi-user behavior, and production deployment are not visible in the inspected files.
- JSON-file concurrency, locking, backup, and recovery behavior are not visible.
- The intended production hosting arrangement for the separately served frontend and API is not visible.
