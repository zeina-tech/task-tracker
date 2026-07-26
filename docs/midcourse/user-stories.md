# User Stories — Mid-Course Project

## Feature: Due Dates + Overdue Filter

### Story 1 — Set a due date when creating a task
As a user, I want to optionally set a due date when creating a task, so I can track when it needs to be completed.

**Acceptance criteria:**
- `due_date` is optional on `TaskCreate`
- Accepts a valid ISO 8601 date (e.g. `2026-08-01`)
- Invalid date formats return `422`
- Omitting `due_date` still returns `201` (field is not required)

**AI assumption corrected:** AI initially suggested making `due_date` a `datetime` (date + time). I corrected it to a `date`-only field, since tasks in this tracker are day-level, not time-level, and a full datetime adds unnecessary complexity for Module 1-3's scope.

---

### Story 2 — Update a task's due date
As a user, I want to update or clear a task's due date, so I can adjust deadlines as priorities change.

**Acceptance criteria:**
- `due_date` is optional on `TaskUpdate`
- Sending a new date updates it
- Sending `null` explicitly clears it
- Omitting the field entirely leaves the existing due date unchanged

---

### Story 3 — See which tasks are overdue
As a user, I want the system to tell me which tasks are overdue, so I can prioritize what's late.

**Acceptance criteria:**
- A task is "overdue" if `due_date` is before today's date AND `status != Done`
- Overdue status is computed on read (not stored), so it's always accurate
- `TaskResponse` includes a computed `is_overdue: bool` field

**AI assumption corrected:** AI initially suggested marking a task overdue purely by date, regardless of status. I corrected this — a completed task with a past due date shouldn't display as overdue, since it's finished.

---

### Story 4 — Filter tasks by overdue status
As a user, I want to filter my task list to show only overdue tasks, so I can quickly see what needs attention.

**Acceptance criteria:**
- `GET /tasks?overdue=true` returns only tasks where `is_overdue` is `True`
- `GET /tasks?overdue=false` returns only tasks where `is_overdue` is `False`
- Omitting the `overdue` param returns all tasks (unfiltered), same as current behavior
- No matches returns `200` with `[]`, not `404`

---

### Story 5 — See due dates and overdue indicators in the Kanban board
As a user, I want to see a task's due date on its card, and a visual indicator if it's overdue, so I don't have to open each task to check.

**Acceptance criteria:**
- Task cards display the due date if one is set
- Overdue tasks show a distinct visual pill/badge (e.g. red "Overdue" label)
- Tasks with no due date show no date-related UI (no blank/placeholder clutter)

## Feature: Search + Combined Filters

### Story 1 — Search tasks by title or description
As a user, I want to search my tasks by keyword, so I can quickly find a specific task without scrolling.

**Acceptance criteria:**
- `GET /tasks?search=<text>` returns tasks where the search text appears in `title` OR `description`
- Search is case-insensitive
- No matches returns `200` with `[]`
- Omitting `search` returns all tasks, unfiltered

**AI assumption corrected:** AI initially suggested search should only match `title`. I corrected it to also match `description`, since relevant tasks can be found by their details, not just their title.

---

### Story 2 — Combine search with existing filters
As a user, I want to combine search with status and priority filters, so I can narrow results precisely.

**Acceptance criteria:**
- `GET /tasks?search=<text>&status=<status>&priority=<priority>` applies all filters together (AND logic, not OR)
- Any combination of `search`, `status`, `priority` (and `overdue`, once implemented) can be used together
- An invalid `status` or `priority` value still returns `422` (existing enum validation behavior is preserved)

---

### Story 3 — Empty and no-match states stay predictable
As a user, I want the task list to behave consistently even when no tasks match my filters, so the UI doesn't break or show errors.

**Acceptance criteria:**
- Any combination of filters with zero matches returns `200` and `[]`
- The system never returns `404` for a list endpoint, regardless of filter combination

---

### Story 4 — Search bar visible above the Kanban board
As a user, I want a search/filter bar above my Kanban board, so I can narrow down visible tasks without leaving the board view.

**Acceptance criteria:**
- A search input and filter controls appear above the Kanban columns
- Kanban columns remain visible even when filters are active (columns don't disappear, just show fewer/no cards)
- Empty columns display a clear "no tasks" state rather than looking broken