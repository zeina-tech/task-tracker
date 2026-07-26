# Prompt Log — Mid-Course Project

## Feature: Due Dates + Overdue Filter

### Prompt 1 — Model changes
**Prompt:** "Add due_date to TaskCreate, TaskUpdate, and TaskResponse. Store as a
date (not datetime). Add a computed is_overdue field to TaskResponse."

**AI response summary:** Added `due_date: Optional[date] = None` to all three
models, plus `is_overdue: bool` as a required field on `TaskResponse`.

**Accepted / Edited / Rejected:** Accepted as-is. This was a small, well-scoped
change that matched the ADR exactly.

---

### Prompt 2 — Storage logic
**Prompt:** "Update storage.py's add_task() and update_task() to compute
is_overdue based on due_date and status, per the rule: overdue only if
due_date is past AND status != Done."

**AI response summary:** Added a `_compute_is_overdue()` helper used in both
`add_task` and `update_task`, so the value is always recalculated on write
rather than trusted from client input.

**Accepted / Edited / Rejected:** Accepted. This centralized the logic in one
place instead of duplicating the check in two functions, which was a better
design than what I initially asked for (I hadn't specified a shared helper).

---

### Prompt 3 — Debugging a masked error
**Prompt (informal, in response to broken tests):** "why do I get 409 on
task creation now?"

**AI response summary:** Diagnosed that `TaskResponse` now required
`due_date`/`is_overdue`, but `storage.add_task()` didn't supply them —
causing a Pydantic `ValidationError`. Because `ValidationError` is a subclass
of `ValueError`, and the route's `except ValueError` was written to catch
duplicate-task conflicts, the real error was silently mislabeled as a `409`.

**Accepted / Edited / Rejected:** Accepted the diagnosis and the fix (adding
the missing fields to the `TaskResponse` construction, and narrowing the
exception handler to a specific `DuplicateTaskError` class instead of a
generic `ValueError`). This was the most valuable moment in the whole
project — the bug wasn't in the new code I was adding, it was a
pre-existing fragile exception handler that only broke because of an
unrelated change. I would not have found this without asking the AI to
trace the actual stack trace rather than guessing.

---

### Weak prompt → Strong prompt rewrite

**Weak prompt (what I might have asked first):**
"Add due dates to my task tracker."

**Why it's weak:** No model spec, no validation rules, no storage behavior,
no constraints on what NOT to touch. This would produce a plausible-looking
but under-specified change — likely missing the overdue computation rule,
or picking `datetime` instead of `date`, or not stating that `Done` tasks
should never show as overdue.

**Strong prompt (what I actually used):**
"Add due_date to TaskCreate, TaskUpdate, and TaskResponse. Store as a date
(not datetime). Add a computed is_overdue field to TaskResponse, computed
as: due_date < today AND status != Done. Do not modify unrelated routes."

**Why it's stronger:** Specifies exact field types, the exact business rule
for the computed field, and an explicit boundary on what not to touch —
consistent with the small-scoped-prompt pattern used throughout Modules 1-2.

---

## Feature: Search + Combined Filters

### Prompt 1 — Storage support
**Prompt:** "Add optional overdue and search params to storage.get_all_tasks().
search should match title OR description, case-insensitive. All filters
combine with AND logic."

**AI response summary:** Added `overdue: Optional[bool]` and
`search: Optional[str]` params, applied as sequential filters after
`status`/`priority`, using substring matching on lowercased `title`/`description`.

**Accepted / Edited / Rejected:** Accepted as-is.

---

### Prompt 2 — Route wiring
**Prompt:** "Add overdue and search query params to GET /tasks in main.py."

**AI response summary:** Provided a replacement for the `list_tasks` route
signature and body.

**Accepted / Edited / Rejected:** Edited — my own copy/paste error left two
copies of `list_tasks` in the file (one old, one new) and accidentally
deleted the `POST /tasks` route entirely in the process. Caught via a full
`Get-Content app/main.py` review and a failing `curl` test showing
`405 Method Not Allowed`, then manually corrected by replacing the entire
duplicated block with a single clean version of both routes.

---

### Prompt 3 — Frontend integration
**Prompt:** "Add a search input and status/priority/overdue filter dropdowns
above the Kanban board. Wire them to GET /tasks with debounced search input."

**AI response summary:** Provided CSS for a `.filter-bar`, HTML for the
search input and three dropdowns, and JS to build a query string from
current filter values, refactoring `fetchTasks()` to use it.

**Accepted / Edited / Rejected:** Accepted the structure, but had to debug
in follow-up: a missing `const dueDateInput` declaration (from the earlier
due-date feature, not this one) caused a `ReferenceError` when opening the
edit modal, unrelated to the search feature itself but surfaced during this
testing pass. Fixed by adding the missing declaration.