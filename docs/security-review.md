# Security Review

## AI Findings

| ID | Severity | File / location | Finding | Evidence | Suggested next step | Confidence | Grade | Reason |
|---|---|---|---|---|---|---|---|---|
| SEC-01 | Medium | `app/models.py:24-27`, `:55-60`; `app/main.py:69-94` | Several client-controlled strings are unbounded, enabling disproportionate memory, disk, and CPU use. | Only `title` has a 200-character validator. `description`, `assignee`, and `search` have no maximum length; search scans every in-memory task and list responses have no pagination. | Add suitable `max_length` limits and bound `search`; introduce pagination or a result cap before this is used beyond its learning scope. | High | Valid | Title is limited by 200 characters whereas `description`, `assignee`, and `search` have no maximum length. So a client really could send a multi-megabyte string for either field and Pydantic would accept it. I think severity is rather low as per the application usage. |
| SEC-02 | Medium | `app/storage.py:14-28`, `:37`, `:86-87`, `:163-165`, `:178-180` | JSON persistence is neither atomic nor synchronized, risking lost updates or a corrupted task file under concurrent requests or multiple app processes. | Module-level `_tasks` is loaded once; every mutation rewrites the same file with `write_text()` directly, with no lock, temporary file, or atomic replace. | For any multi-user/deployed use, use transactional storage; at minimum add process-safe locking and atomic write/replace with recovery handling. | High | Valid | Confirmed in app/storage.py: _tasks loads once into memory and every mutation overwrites tasks.json directly with no lock or atomic write. Because storage functions run in FastAPI's thread pool, even a single user sending overlapping requests can trigger a race where one write silently overwrites another. |
| SEC-03 | Low | `.dockerignore:55-56`; `Dockerfile:22-29` | Containerized task data is not included in the image and no persistence mechanism is configured or documented. Task records can be lost when a container is recreated. | `data/` is excluded from the Docker build context, while storage writes to `/app/data/tasks.json` at runtime. No volume is declared. | Document and configure a persistent mounted volume if Docker is intended to retain user data. | High | Noise | .dockerignore excludes data/ from the image and no VOLUME is declared, so task data doesn't survive container recreation. This is accurate but fits with the course requirements: the project's Docker requirement only asks for build/run//health verification, not persistence across restarts. |
| SEC-04 | Low | `Dockerfile:4,15`; `.github/workflows/ci.yml:15,17,21,29-32`; `requirements.txt:1-6` | Build/CI dependency integrity is only partially pinned. | Direct Python packages are version-pinned, but installs do not require hashes; Docker base images use mutable tags and GitHub Actions use mutable major-version tags. | Pin container images by digest, GitHub Actions by commit SHA, and adopt a hash-locked dependency workflow if supply-chain integrity is required. | High | Noise | Out of the Project's scopre |
| SEC-05 | Informational | `app/main.py:42-175`; `AGENTS.md:21`; `CLAUDE.md:89-93` | All task data and mutation endpoints are unauthenticated. This is an explicit course-scope decision, not a defect to change for Module 5. | Routes expose create, read, update, and delete without access checks. Project instructions explicitly prohibit adding authentication/authorization. | Keep the service limited to the intended local learning environment; reassess authentication and authorization before any shared or internet-facing deployment. | High | Valid | no route in app/main.py has an auth dependency, and this matches the course's explicit rule against adding authentication. Informational point that fits with the project's scope and boundaries. |

## My Manual Findings

| Severity | File:Line | Finding | Suggested Fix | Reason |
|---|---|---|---|---|
| Informational | `Dockerfile:8,20-23` | Container already runs as non-root user `app` (uid 1000), with `/app` ownership explicitly set via `chown` before `USER app` is declared. | None — already implemented correctly; no fix needed. | Manually checked container process privileges since this wasn't something the AI security review flagged; confirms no gap exists here. |

## Reconciliation

### Agreement
All 5 AI findings (SEC-01 through SEC-05) were checked against the actual code and confirmed accurate. The AI correctly described what exists in `app/models.py`, `app/main.py`, `app/storage.py`, `Dockerfile`, `.dockerignore`, `requirements.txt`, and `.github/workflows/ci.yml`. No finding was wrong.

### AI-only
SEC-03 (no Docker volume for task persistence) and SEC-04 (dependencies pinned by version but not by hash/SHA) were flagged by the AI but graded Noise — both are technically accurate but out of scope for this project's stated requirements (local, non-deployed learning app; Docker requirement only asks for build/run/`/health` verification).

### You-only
A manual check of the `Dockerfile` confirmed the container already runs as a non-root user (`app`, uid 1000) with correct file ownership set before `USER app` — something the AI security review did not flag either way. This wasn't a gap; it confirmed an existing good practice the automated review missed entirely.

## Top 3 Unfixed Backlog

| Rank | Finding | Severity | Owner | Next Step |
|---|---|---|---|---|
| 1 | SEC-02: In-memory task store overwrites `tasks.json` on every mutation with no lock or atomic write; concurrent requests can race and silently lose an update. | Medium | You | Add a lock (e.g. `threading.Lock`) around mutation/save calls, or move to atomic write (temp file + `os.replace`) if pursued after the course. |
| 2 | SEC-01: `description` and `assignee` fields have no `max_length`; `GET /tasks` has no pagination and `search` scans the full task set unbounded. | Low–Medium | You | Add `Field(max_length=...)` to both fields and `limit`/`offset` params to `/tasks` if pursued after the course. |
| 3 | SEC-04: CI actions pinned by mutable tag, dependencies version-pinned but not hash-locked. | Low | You | Pin GitHub Actions by commit SHA and adopt hash-locked installs if this project were ever deployed with real users or secrets. |
