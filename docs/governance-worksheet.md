# Governance Retrospective - AI-Assisted Coding

## What I Shared With AI

| Item | Module | Risk Level | Reason |
|---|---|---|---|
| Task Tracker code | 2-5 | Low | Course-generated code intended for a public repo for instructor grading; no real secrets or credentials, and all task data used is fabricated by me for testing, not real user/customer data. |
| Test output and stack traces | 2-4 | Low | Included local file paths from my machine within tracebacks, but no credentials, tokens, or real data — file paths alone pose minimal exposure risk. |
| Frontend code | 3 | Low | Course-generated Kanban board code with no hardcoded API keys, credentials, or personal information. |
| Dockerfile and CI YAML | 4 | Low | Only plain file contents were shared — no secrets, credentials, org names, or identifying details; confirmed via security review that `.dockerignore` excludes secrets/env files and no credentials are baked into either file. |
| Any real external data I used by mistake | N/A | Low | No real external or personal data was ever shared with AI tools throughout the course — all task data used for testing was fabricated. |

## AI Risk Classification

| Item | Module | Risk Level | Reason |
|---|---|---|---|
| Task Tracker code | 2-5 | Low | Course-generated, authorized-for-sharing code with fabricated task data and no secrets fits the toy-project category. |
| Test output and stack traces | 2-4 | Low | Local file paths without credentials, tokens, or real data pose minimal exposure risk. |
| Frontend code | 3 | Low | The course Kanban frontend contains no hardcoded keys, credentials, or personal information. |
| Dockerfile and CI YAML | 4 | Low | Plain configuration without embedded secrets or identifying internal details is low-risk to share. |
| Any real external data I used by mistake | N/A | Low | No real external or personal data was shared, so there is no sensitive-data exposure in this category. |

## What I Received From AI

| Generated Thing | Module | Do I Understand It Line by Line? | Action |
|---|---|---|---|
| Backend models and validators | 2 | Partially | Coming from a MATLAB/engineering and Python-for-ML background, many FastAPI/Pydantic-specific concepts (decorators like `field_validator`, type hints such as `Optional`, model classes) were new. I researched these terms individually to understand the underlying concept before accepting the generated code, rather than accepting it blindly. |
| Frontend board and drag-and-drop logic | 3 | Partially | JavaScript drag-and-drop concepts and event handling were unfamiliar coming from a MATLAB/Python background; researching these terms took longer than the time allotted for the module, but I worked through them before accepting the generated code. |
| CI workflow | 4 | Partially | GitHub Actions syntax and concepts (jobs, steps, caching, triggers) were unfamiliar; I followed along with AI step by step to complete the workflow rather than researching independently, so my understanding is functional but not yet independent. |
| Dockerfile | 4 | Partially | Multi-stage build structure, `USER`, and `HEALTHCHECK` concepts were unfamiliar; I followed along with AI to complete the Dockerfile rather than researching independently, so my understanding is functional but not yet independent. |
| Security findings and plans | 5 | Yes | Verified each of the 5 AI security findings against the actual code in `app/models.py`, `app/main.py`, `app/storage.py`, `Dockerfile`, and `requirements.txt` before grading; corrected my own initial framing of one finding (concurrency risk, not "multi-user") and made independent scope/severity judgments rather than accepting the AI's grading as given. |
