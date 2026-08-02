# Architecture Context-Strategy Comparison

| Strategy | What it got right | What it got wrong, missed, or invented | Best suited task shape |
|---|---|---|---|
| A - minimal context | Produced the most complete implementation-oriented draft: API, frontend flow, storage, business rules, tests, and data file are all represented. It named its inspected files and isolated its production-suitability comment as an inference. | Its breadth required reading twelve files, so it is not truly minimal in execution. It says the frontend is served on port 8080 as an assumption and adds a production caveat that it acknowledges is inferred rather than directly stated. | Broad repo documentation when the agent may inspect freely and the task benefits from a discovery pass. |
| B - structured context | Kept the same broad coverage as A while making conventions clearer: validation, storage, error handling, and frontend/backend interaction are separately stated. It explicitly lists unconfirmed areas rather than presenting them as facts. | The supplied Strategy B prompt names "file summaries," but none appear in the visible context; the result still depended on inspecting many implementation files. Its claim that `AGENTS.md` established the JSON-storage constraint overstates that file's role, since the draft itself says implementation files supplied app-specific details. | Architecture or governance documentation where project rules and fixed vocabulary must guide a wider repository read. |
| C - targeted context | Followed the three-file boundary and consistently used "not visible from the files I read." It accurately limited claims about the frontend, status-transition rules, tests, deployment, logging, and concurrency. | It could not fully satisfy a repo-wide architecture brief: its create flow begins with an unspecified client, and its frontend discussion is necessarily incomplete. It lists `app/business_rules.py` and `data/tasks.json` as key files without reading them, although it carefully labels their contents as not visible. | Focused backend/API analysis, especially when evidence boundaries matter more than complete system coverage. |

## Verdict

I chose Strategy B for the final architecture document because it combines the wide coverage needed for a repo-level architecture description with explicit project guardrails and a clear separation between confirmed behavior and items not visible. Strategy A reaches a similar result but relies on a less constrained discovery pass, while Strategy C is more disciplined than complete for a document that must describe the frontend and cross-file conventions.

## Context-engineering rule

For a repo-wide architecture document with fixed project rules and several required sections, I use Strategy B because it supplies the governing constraints while still allowing evidence-based inspection across the relevant implementation files.

For a narrowly scoped backend or API question where unsupported claims are the main risk, I use Strategy C because its anchor-file boundary makes missing evidence explicit.
