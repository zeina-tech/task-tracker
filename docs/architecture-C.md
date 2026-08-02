# Task Tracker Architecture

## What the app does

Task Tracker is a FastAPI REST API for creating, listing, retrieving, updating, and deleting tasks. It persists tasks to a JSON file and exposes a health-check endpoint.

## Data model

`Task` data is represented through Pydantic request/response models.

- `TaskCreate`: `title`, `description`, `status`, `priority`, `assignee`, `due_date`
- `TaskUpdate`: optional versions of the mutable task fields
- `TaskResponse`: task fields plus generated `id`, computed `is_overdue`, `created_at`, and `updated_at`
- Status values: `ToDo`, `InProgress`, `Done`
- Priority values: `Low`, `Medium`, `High`

## Request flow: create a task

1. A client sends `POST /tasks`; FastAPI parses the body as `TaskCreate`.
2. Pydantic rejects unknown fields and validates the title by trimming it, requiring a non-blank value, and limiting it to 200 characters.
3. `storage.add_task` checks for an existing task with the same title, description, status, priority, and assignee.
4. If unique, storage generates a UUID, timestamps the task in UTC, computes `is_overdue`, writes all tasks to `data/tasks.json`, and returns the new task with HTTP 201.
5. A duplicate produces HTTP 409 with `Task already exists`.

## Key files

- `app/main.py` — FastAPI app setup, CORS configuration, and task API routes.
- `app/models.py` — task enums and Pydantic request/response validation models.
- `app/storage.py` — in-memory task collection, JSON persistence, CRUD operations, and overdue calculation.
- `app/business_rules.py` — referenced for status-transition validation; its contents are not visible from the files I read.
- `data/tasks.json` — referenced as the JSON persistence target; its current contents are not visible from the files I read.

## Conventions

- **Validation:** request models forbid extra fields; task titles are trimmed, required, and limited to 200 characters.
- **Storage:** tasks load into an in-memory dictionary at startup and the complete collection is rewritten to JSON after create, update, or delete.
- **Error handling:** missing tasks return HTTP 404; duplicate creation returns HTTP 409; status-transition handling is not visible from the files I read.
- **Frontend/backend interaction:** the API permits CORS requests from `http://localhost:8080` and `http://127.0.0.1:8080`; frontend implementation is not visible from the files I read.

## Not visible or assumptions

- Status-transition rules are not visible from the files I read.
- The frontend’s files, behavior, and exact API calls are not visible from the files I read.
- Authentication, authorization, deployment configuration, tests, logging, and concurrency behavior are not visible from the files I read.
- The schema and current data in `data/tasks.json` are not visible from the files I read.
