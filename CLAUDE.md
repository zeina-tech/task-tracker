# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A learning-focused Task Tracker: FastAPI + Pydantic v2 backend with JSON-file
storage (`data/tasks.json`), and a single-file HTML/CSS/JS Kanban frontend
(`frontend/index.html`). No database — see `docs/midcourse/mini-adr.md` for
why (keeps the project small and consistent with the original ADR-001
constraints: extend existing patterns, avoid new dependencies/architecture).

## Commands

Activate the venv first (`venv\Scripts\Activate.ps1` on Windows,
`source venv/bin/activate` on Linux/macOS).

- Run backend: `python -m uvicorn app.main:app --reload --port 8000` (serves at `http://localhost:8000`, docs at `/docs`)
- Run frontend: `cd frontend && python -m http.server 8080` (separate terminal, backend must be running; expects backend on `localhost:8000`, CORS configured in `app/main.py` for `localhost:8080`)
- Run all tests: `python -m pytest -v`
- Run a single test file: `python -m pytest tests/test_tasks.py -v`
- Run a single test: `python -m pytest tests/test_tasks.py::test_name -v`

## Architecture

- `app/main.py` — FastAPI routes only; delegates persistence to `storage.py` and status-transition checks to `business_rules.py`.
- `app/models.py` — Pydantic models. `TaskCreate`/`TaskUpdate` are input models (`extra="forbid"`); `TaskResponse` is the output model and includes `is_overdue`, which is **not** a stored field.
- `app/storage.py` — Module-level `_tasks` dict is the in-memory source of truth, loaded from and persisted to `data/tasks.json` on every mutation. `is_overdue` is computed at read time (`_compute_is_overdue`) from `due_date` and `status`, never persisted, so it can't go stale as time passes.
- `app/business_rules.py` — `VALID_TRANSITIONS` is the single allowed-status-transition table (ToDo→InProgress→Done, and Done→InProgress for reopening). Same→same and any transition not in this set is rejected with 422.
- Duplicate detection: a task is a duplicate (409) if `title`, `description`, `status`, `priority`, and `assignee` all match an existing task — checked in `storage.add_task`.
- `GET /tasks` filters (`status`, `priority`, `overdue`, `search`) are applied incrementally in `storage.get_all_tasks` and combine with AND logic; `search` is a case-insensitive substring match against `title` OR `description`.
- Tests use FastAPI's `TestClient` against the real `app`; `tests/conftest.py`'s autouse `_reset_storage` fixture clears `storage._tasks` before and after every test, so tests don't leak state through `data/tasks.json`.

## Design decisions worth knowing before changing behavior

See `docs/midcourse/mini-adr.md` for full reasoning. Key ones:
- `due_date` is a plain `date` (no time-of-day, no timezone) — deliberate, not an oversight.
- `is_overdue` is always computed, never stored.
- Filters combine with AND, not OR.
- No full-text/fuzzy search library — plain substring match is intentional for this project's scope.
