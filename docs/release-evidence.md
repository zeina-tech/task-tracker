# Release Evidence

## Baseline
- Branch: final-project
- Date: 2 August 2026
- Local app run command: `uvicorn app.main:app --reload`
- /health result: 200 OK — `{"status":"ok","timestamp":"2026-08-02T17:21:14.513525+00:00"}`
- Frontend check: Served from `frontend/` via `python -m http.server 8080`, opened at `http://localhost:8080` (backend running separately on `http://localhost:8000`); Kanban board and create/edit flow confirmed functioning.
- Test command: `pytest -v --tb=short`
- Test result: 33 passed in 0.26s, no failures

## CI evidence
- Workflow file: `.github/workflows/ci.yml`
- Latest run link or note: https://github.com/zeina-tech/task-tracker/actions/runs/30758897509 — CI #2, commit `5be9860`, branch `final-project`, succeeded in 28s (Aug 2, 2026, 8:27 PM GMT+3)
- Test command used by CI: `pytest -v --tb=short`
- Shortcut check: no `continue-on-error`, no `|| true`, pytest is not skipped; Python version pinned to `3.11`, dependencies installed via `pip install -r requirements.txt` before tests run.

## Docker evidence
- Build command: `docker build -t task-tracker .`
- Run command: `docker run -p 8000:8000 task-tracker`
- /health check: 200 OK — confirmed both from container logs (`GET /health HTTP/1.1" 200 OK`) and from host via `Invoke-WebRequest http://localhost:8000/health -UseBasicParsing`, response `{"status":"ok","timestamp":"2026-08-02T22:00:52.489183+00:00"}`
- Non-root check: confirmed — container runs as non-root user `app` (uid 1000), with `chown -R app:app /app` applied before `USER app` is set in the Dockerfile.
- No-baked-secrets check: confirmed — `.dockerignore` excludes `.env`, `.env.*`, `*.pem`, `*.key`, `credentials*`, `secrets*`, `token*`.

## Documentation claim-vs-reality log

| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| README's local run command actually starts the API | Ran `uvicorn app.main:app --reload` | Confirmed — server started, `/health` returned 200 | None needed |
| `/health` endpoint returns HTTP 200 with a status/timestamp body | `Invoke-WebRequest` against running server and running container | Confirmed both locally and in Docker — `{"status":"ok","timestamp":...}` | None needed |
| Docker image builds and runs with `/health` responding 200 | `docker build` + `docker run` + `Invoke-WebRequest` | Confirmed — 200 OK from container | None needed |