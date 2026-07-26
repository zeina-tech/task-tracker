# Mini-ADR — Mid-Course Project

## Title
Mid-Course ADR: Due Dates + Overdue Filter, and Search + Combined Filters

## Status
Accepted

## Context
This project extends the existing Task Tracker (Modules 1-3), which currently
supports full CRUD on tasks with `title`, `description`, `status`, `priority`,
and `assignee`, backed by in-memory storage and Pydantic v2 validation. Two
new features are being added for the mid-course checkpoint:

1. Due dates on tasks, with an overdue filter
2. Search by keyword, combinable with existing status/priority filters

Both features must extend the existing architecture (Pydantic models, in-memory
storage, FastAPI routes) without introducing a database, external services, or
significant new dependencies, consistent with ADR-001's original constraints.

## Decision

### Due dates
- Add `due_date: Optional[date] = None` to `TaskCreate`, `TaskUpdate`, and
  `TaskResponse`.
- Store `due_date` as a plain `date` (day-level precision), not `datetime`,
  since the tracker does not need time-of-day granularity.
- Compute `is_overdue` as a derived field at read time (not stored), based on
  `due_date < today AND status != Done`. This avoids storage getting out of
  sync with the current date.
- Add an optional `overdue: bool` query parameter to `GET /tasks` to filter
  by computed overdue status.

### Search + combined filters
- Add an optional `search: str` query parameter to `GET /tasks`.
- Search matches (case-insensitive substring match) against `title` OR
  `description`.
- All query parameters (`status`, `priority`, `search`, `overdue`) combine
  with AND logic — filtering is applied incrementally in `storage.py`,
  consistent with the existing `get_all_tasks(status, priority)` pattern.
- No new dependencies required; substring search uses Python's built-in
  string methods.

## Reasoning
Both features were chosen because they extend the existing storage and
validation patterns directly:
- `due_date` follows the same optional-field pattern as `assignee`.
- Filtering follows the same pattern already used for `status` and
  `priority` in `storage.get_all_tasks()`.

This keeps the two features small, testable, and consistent with the
project's existing architecture and learning goals, rather than introducing
new patterns or technologies.

## Alternatives Considered

**Storing `is_overdue` as a persisted field, updated on write.**
Rejected — this risks the stored value going stale (a task doesn't "become"
overdue through any write operation; time simply passes). Computing it at
read time guarantees correctness without needing a background job or
scheduled task.

**Full-text search library (e.g. a fuzzy-matching or indexing library).**
AI suggested this as an option for the search feature. Rejected as
out-of-scope — a substring match is sufficient for the task list sizes this
project supports, and adding a search library increases dependencies without
meeting a real requirement at this stage.

**Time-zone-aware `datetime` due dates.**
AI's first draft of the due-date model used `datetime` with timezone
handling. Rejected in favor of a plain `date` — timezone correctness adds
real complexity that isn't warranted for a day-level due date in a
single-user learning project.

**OR logic for combined filters (any filter matches).**
Considered briefly, but rejected — AND logic is the expected behavior for
"narrowing down" a list (e.g. "status=Done AND priority=High"), and matches
how filter UIs conventionally behave.

## Consequences

**Positive**
- Both features reuse existing patterns (`Optional` fields, incremental
  filtering in `storage.py`), keeping the codebase consistent.
- `is_overdue` computed at read time is always accurate, with no risk of
  stale data.
- No new dependencies or architecture changes required.

**Negative**
- Substring search is simple and will not handle typos, stemming, or
  relevance ranking — acceptable for this project's scope.
- Computing `is_overdue` on every read is a minor CPU cost, but negligible
  at this project's scale (in-memory storage, small task counts).