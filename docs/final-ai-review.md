# Final AI Review and Ownership Evidence


## AGENTS.md guardrails
- Repo-specific stack and commands included: Yes — stack (Python 3.11, FastAPI, Pydantic v2, pytest) and exact run/test commands (`uvicorn app.main:app --reload`, `pytest -v`) are listed.
- Docs-first/read-first guardrail included: Yes — "Prefer read-only analysis first," restricts edits to `docs/` without explicit approval, and requires stating which files were read before a repo-grounded answer.
- Unexpected app/frontend edits rule included: Yes — explicitly states "Do not edit `app/` while doing security review, governance, feature planning, architecture docs, or playbook work."

## AI code review mini-log

## AI code review mini-log

Reviewed commit `316c1ff` ("Add Google-style docstrings to public functions and route
handlers") in `app/business_rules.py`, `app/main.py`, `app/models.py`, and
`app/storage.py`.

| AI comment | Grade: Useful / Noise / Wrong | Reason | Verification or decision |
|---|---|---|---|
| Docstring examples use untested `>>>` doctest syntax; CI never runs them (`pytest -v --tb=short`, no `--doctest-modules`). | Useful | Project is finished and unlikely to change, so risk of examples becoming inaccurate over time is low but still a noted limitation. | Accepted as-is. |
| `create_task`'s docstring claims `HTTPException 409` on duplicate, but the diff's context window cuts off before the `raise` line, so the claim couldn't be confirmed from the diff alone. | Noise | Checked the actual file — claim is accurate (`raise HTTPException(status_code=409, ...)` confirmed). AI's caution was reasonable given the incomplete diff, but not an actual defect once verified. | Confirmed correct; no change needed. |
| Commit message claims docstrings were added "without changing any logic"; diff has no `-` lines removing existing code, only `+` lines adding docstring text. | Noise | The diff visually makes this obvious on inspection — stating it explicitly adds little for a reviewer already looking at the diff. | Confirmed accurate; no action needed. |
| Docstrings consistently follow Google-style structure (Args/Returns/Raises) across all four touched files. | Noise | Consistency is the expected outcome of one AI session following one prompt across a single pass, not a meaningfully uncertain thing worth confirming. | Confirmed accurate; not a notable finding. |

## AI security mini-review

| Finding | File evidence | Grade: Valid / False Positive / Noise | Reason | Next action |
|---|---|---|---|---|
| SEC-01: `description`/`assignee` have no `max_length`; `GET /tasks` has no pagination and `search` scans the full task set unbounded. | `app/models.py` (TaskCreate/TaskUpdate fields), `app/main.py` (`list_tasks` route) | Valid | Confirmed both claims directly against the code — no validator or length limit on either field, no `limit`/`offset` params on the route. | Documented for backlog; no `app/` change made, consistent with project scope to protect existing app code. |
| SEC-02: In-memory task store overwrites `tasks.json` on every mutation with no lock or atomic write; concurrent requests can race and lose an update. | `app/storage.py` (`_load_tasks`, `_save_tasks`, `add_task`, `update_task`, `delete_task`) | Valid | Confirmed `_tasks` loads once at import and every mutation calls `_save_tasks()`, which overwrites the file directly. Because storage functions run in FastAPI's thread pool, concurrent requests can race even with a single user. | Documented for backlog; no `app/` change made, consistent with project scope. |
| SEC-03: No Docker volume declared; task data does not persist across container recreation. | `.dockerignore` (excludes `data/`), `Dockerfile` (no `VOLUME`) | Noise | Confirmed accurate, but out of scope — the project's Docker requirement only asks for build/run/`/health` verification, not persistence across restarts. | No action needed; documented as a known limitation for future deployment. |
| SEC-04: CI actions pinned by mutable version tag, not SHA; dependencies version-pinned but not hash-locked. | `.github/workflows/ci.yml` (`actions/checkout@v4`, etc.), `requirements.txt` (`==` pins, no hashes) | Noise | Confirmed accurate, but SHA/hash-pinning is a production supply-chain hardening practice disproportionate to this project's local, non-deployed learning scope. | No action needed; documented as a deliberate scope trade-off. |
| SEC-05: No authentication on any endpoint. | `app/main.py` (no auth dependency on any route), `AGENTS.md` ("Do not add authentication or a database in Module 5") | Valid, informational only | Confirmed no route has an auth dependency; matches the explicit course rule against adding authentication. Not a defect — a deliberate, instructor-mandated scope boundary. | No action — authentication is explicitly out of scope per course rules. |

## Manual security check

Checked container process privileges in `Dockerfile` since this was not something the AI
security review flagged either way. Confirmed the container already runs as a non-root
user (`app`, uid 1000), with `/app` ownership explicitly set via `chown` before `USER app`
is declared (`Dockerfile:8,20-23`). No gap found — this check confirmed an existing good
practice rather than surfacing a new issue.

## Reconciliation

### Agreement
All 5 AI security findings (SEC-01 through SEC-05) were checked against the actual code
and confirmed factually accurate — the AI correctly described what exists in
`app/models.py`, `app/main.py`, `app/storage.py`, `Dockerfile`, `.dockerignore`,
`requirements.txt`, and `.github/workflows/ci.yml`. No finding was factually wrong.

### AI-only
SEC-03 (no Docker volume for task persistence) and SEC-04 (dependencies pinned by version
but not by hash/SHA) were flagged by the AI but graded Noise — both are technically
accurate but out of scope for this project's stated requirements.

### You-only
A manual check of the `Dockerfile` confirmed the container already runs as a non-root
user with correct file ownership — something the AI security review did not flag either
way. This wasn't a gap; it confirmed an existing good practice the automated review
missed entirely.


## One AI output I rejected or corrected

The AI review flagged that `create_task`'s docstring claim of raising `HTTPException 409`
on duplicate creation could not be confirmed from the diff alone, since Git's context
window cut off before the actual `raise` line. Rather than accept this as an open concern,
I checked the full function in `app/main.py` directly and confirmed the `except` block
does raise `HTTPException(status_code=409, detail="Task already exists")` exactly as the
docstring states. I downgraded this from an open question to Noise once verified, rather
than leaving it flagged or assuming the AI's caution meant something was actually wrong.

## Three AI usage rules

1. Never paste: real credentials, tokens, `.env` values, or real user/customer data —
   and generalize local file paths before pasting stack traces or generated docs.
2. Always verify: check AI-generated findings, code, or config against the actual file
   and line it references before accepting it, rather than trusting the AI's description.
3. Record AI contributions by: logging what AI generated or suggested, grading it
   (Valid/Noise/False Positive or Useful/Noise/Wrong), and stating the reason in docs/
   files rather than relying on memory or an unlogged chat history.

## Ownership statement

## Ownership statement

I'm comfortable submitting this repo because every AI-generated finding, plan, and code
change in it was checked against the real files before I accepted it, not taken on trust.
Coming from a MATLAB and Python-for-ML background rather than web development, I closed
real gaps in my knowledge by looking up unfamiliar concepts rather than accepting code I
couldn't explain, and when I hit a real bug myself — the same task appearing twice on the
Kanban board — I identified the cause and had a duplicate check added. I also caught a
case where the AI's own self-critique of a feature plan found zero issues across six
sections and treated that as a signal to look harder rather than accept it at face value,
which a second pass confirmed was warranted. I can walk through and defend every command,
finding, and decision recorded in this repo's docs/.