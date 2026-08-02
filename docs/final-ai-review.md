# Final AI Review and Ownership Evidence

## AGENTS.md guardrails
- Repo-specific stack and commands included: yes/no — TODO: confirm AGENTS.md lists exact run/test commands
- Docs-first/read-first guardrail included: yes/no — TODO
- Unexpected app/frontend edits rule included: yes/no — TODO

## AI code review mini-log

TODO — choose one real diff or changed file, record at least 3 AI review comments,
grade each Useful / Noise / Wrong with a reason.

| AI comment | Grade: Useful / Noise / Wrong | Reason | Verification or decision |
|---|---|---|---|
| | | | |
| | | | |
| | | | |

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

TODO — draft option: the AI's own first-pass self-critique of the Module 5.4
comments-feature plan labeled all six sections "Right" with zero findings. This was
rejected as insufficiently critical — a second, independent pass found at least one real
gap (no handling or test for concurrent comment writes, given the same lock-free storage
pattern flagged in SEC-02). Confirm if you want to use this example or a different one.

## Three AI usage rules

1. Never paste: real credentials, tokens, `.env` values, or real user/customer data —
   and generalize local file paths before pasting stack traces or generated docs.
2. Always verify: check AI-generated findings, code, or config against the actual file
   and line it references before accepting it, rather than trusting the AI's description.
3. Record AI contributions by: logging what AI generated or suggested, grading it
   (Valid/Noise/False Positive or Useful/Noise/Wrong), and stating the reason in docs/
   files rather than relying on memory or an unlogged chat history.

## Ownership statement

TODO — 3-5 sentences in your own words.