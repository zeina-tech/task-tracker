# Verification — Mid-Course Project

## Baseline Check

Before starting Feature 1 (Due Dates), the existing test suite was run to
confirm a clean starting point:

python -m pytest -v
================================= test session starts ==================================
collected 21 items
tests/test_health.py::test_health_check_returns_200 PASSED
tests/test_health.py::test_health_check_response_shape PASSED
tests/test_tasks.py:: (19 tests) ... ALL PASSED
================================== 21 passed in 0.13s ===================================

Baseline: **21/21 passing**, 0 failures. This confirmed the Module 1-3
codebase (CRUD, validation, status-transition rules, persistence,
duplicate detection) was stable before any mid-course changes began.

---

## Backend Test Results — After Each Feature

### After Feature 1 (Due Dates + Overdue Filter)

collected 28 items
... (21 original tests) ...
tests/test_tasks.py::test_create_task_with_valid_due_date_returns_201 PASSED
tests/test_tasks.py::test_create_task_with_invalid_due_date_format_returns_422 PASSED
tests/test_tasks.py::test_create_task_with_past_due_date_is_overdue PASSED
tests/test_tasks.py::test_patch_due_date_updates_overdue_status PASSED
tests/test_tasks.py::test_done_task_with_past_due_date_is_not_overdue PASSED
tests/test_tasks.py::test_list_tasks_filter_overdue_true_returns_only_overdue PASSED
tests/test_tasks.py::test_list_tasks_filter_overdue_false_returns_only_non_overdue PASSED
================================== 28 passed in 0.24s ===================================

**+7 new tests, 0 regressions.**

### After Feature 2 (Search + Combined Filters)

collected 33 items
... (28 previous tests) ...
tests/test_tasks.py::test_list_tasks_search_matches_title PASSED
tests/test_tasks.py::test_list_tasks_search_matches_description_case_insensitive PASSED
tests/test_tasks.py::test_list_tasks_search_combined_with_status_filter PASSED
tests/test_tasks.py::test_list_tasks_search_no_matches_returns_200_and_empty_list PASSED
tests/test_tasks.py::test_list_tasks_invalid_status_filter_returns_422 PASSED
================================== 33 passed in 0.24s ===================================
**+5 new tests, 0 regressions.**

**Total new tests added: 12** (requirement was at least 4).

---

## Manual Browser Checks

Performed against the live Kanban UI (`frontend/index.html`, served via
`python -m http.server 8080`) with the backend running on port 8000.

| Check | Result |
|---|---|
| Create task with due date via modal | Due date field saved and displayed correctly on card |
| Edit task to add/change due date | Card updated, `PATCH` succeeded (`200`) |
| Task with past due date, status ≠ Done | Red "Overdue" pill displayed on card |
| Task with past due date, status = Done | No "Overdue" pill (correctly suppressed) |
| Transition task ToDo → InProgress → Done while overdue | Overdue pill disappeared exactly when status became Done |
| Search box, typed "login" | Board narrowed to only matching task after debounce |
| Search box, typed "README" (in description) | Matched via description, case-insensitive |
| Status filter dropdown | Board narrowed to selected status only |
| Overdue filter dropdown | Board narrowed to overdue-only tasks |
| Combined search + status filter | AND logic confirmed — only tasks matching both shown |
| Clear Filters button | Board returned to unfiltered full list |
| New Task after editing another task | Due date field correctly cleared (no leftover value) |

---

## Behavior Contract Before/After Refactor

**Refactor performed:** Replaced the frontend's unconditional inclusion of
`status` in every PATCH payload with conditional inclusion (only sent when
actually changed by the user).

**Before:** Editing any field (e.g. due date only) while leaving Status
unchanged in the dropdown caused the frontend to resend the current status
value. Since the backend's transition rule treats same→same as invalid,
this caused a `422 Unprocessable Content` on *any* edit that didn't also
change status — even unrelated edits like updating a due date.

**After:** `status` is only included in the PATCH payload if the dropdown
value differs from the task's original status when the modal was opened.
Edits to other fields (due date, description, assignee, priority) no
longer trigger unintended transition validation.

**Contract preserved:** Deliberate status changes still go through the
existing transition validation exactly as before — confirmed via manual
retest of ToDo→InProgress→Done and rejected transitions (InProgress→ToDo,
same→same) after the fix, all behaving identically to pre-refactor.

---

## Break Test Evidence

### Break Test 1 — Status-transition validation
**Test targeted:** `test_patch_same_status_returns_422`

**Break:** Commented out the transition-validation call in `update_task()`
in `app/main.py`:
```python
# validate_status_transition(existing.status, payload.status)
```

**Result (actual run):**
tests/test_tasks.py::test_patch_same_status_returns_422 FAILED
def test_patch_same_status_returns_422(client, created_task):
task_id = created_task["id"]
response = client.patch(f"/tasks/{task_id}", json={"status": "ToDo"})

  assert response.status_code == 422

E assert 200 == 422
E + where 200 = <Response [200 OK]>.status_code
1 failed in 0.08s

Confirms the test genuinely exercises the business rule — with validation
disabled, a same-status PATCH incorrectly succeeds instead of being rejected.

**Restored:** Uncommented the line, reran the test:

tests/test_tasks.py::test_patch_same_status_returns_422 PASSED
1 passed in 0.02s

---

### Break Test 2 — Duplicate task detection
**Test targeted:** `test_create_task_duplicate_returns_409`

**Break:** Changed the exception raised in `storage.add_task()` from the
specific `DuplicateTaskError` to a generic `Exception`, without updating
`main.py`'s `except storage.DuplicateTaskError` clause:
```python
raise Exception("Task already exists")  # was: DuplicateTaskError
```

**Result (actual run):**
tests/test_tasks.py::test_create_task_duplicate_returns_409 FAILED
if existing_key == duplicate_key:

  raise Exception("Task already exists")

E Exception: Task already exists
app\storage.py:57: Exception
1 failed in 0.62s

The generic `Exception` was not caught by the route's specific
`except storage.DuplicateTaskError` clause, propagated unhandled through
the full FastAPI/Starlette stack, and surfaced as an unhandled error
instead of the expected `409`. This directly validates a design decision
made earlier in the project: narrowing the exception handler from a broad
`ValueError` to a specific `DuplicateTaskError` class is load-bearing —
a generic exception type would have let this exact class of bug slip
through undetected.

**Restored:** Reverted to `DuplicateTaskError`, reran the test:

tests/test_tasks.py::test_create_task_duplicate_returns_409 PASSED
1 passed in 0.02s


---

### Full suite confirmation after both breaks

collected 33 items
... (all 33 tests) ...
================================== 33 passed in 0.21s ===================================

Confirms both breaks were fully reverted with no side effects — suite
returned to its clean baseline state.

## Final State

- **33/33 automated tests passing**
- **12 new tests** added across the two features (exceeds the 4-test minimum)
- Manual browser verification completed for both features
- One real refactor documented with before/after behavior contract
- Two Break Tests confirm test suite validity, not false positives