
# Technical Decision Note — Documentation Verification Approach
**Project:** Task Tracker (Module 4)
**Status:** DRAFT
**Author:** [Zeina]

## 1. Context

This project documents itself in three places: `README.md` (setup/run/test
instructions and API overview), `CLAUDE.md` (exact run/test commands,
architecture summary, business rules, do-not rules), and inline Google-style
docstrings on route handlers in `app/main.py` (Args/Returns/Raises/Example
per endpoint). A separate file, `docs/midcourse/verification.md`, records
how the mid-course feature work (due dates, search/filters) was actually
verified: a baseline `pytest -v` run (21/21 passing), per-feature test
counts after each change, a manual browser-check table against the live
Kanban UI, a documented before/after behavior contract for one refactor,
and two deliberate "break tests" that disabled a rule or narrowed an
exception type to confirm the corresponding test would actually fail.
`.github/workflows/ci.yml` runs only `pytest -v --tb=short` on push/PR — it
does not execute anything from `docs/midcourse/verification.md`, does not
run the manual browser checks, and does not verify the `>>>` doctest-style
`Example` blocks inside the `app/main.py` docstrings.

## 2. Decision

Documentation correctness for this project is verified by three concrete,
already-performed practices, not by a documentation-linting tool or a doc
test runner:

1. **Automated test suite as ground truth** — every documented behavior
   (status transitions, duplicate detection, filters, search, due dates)
   has a corresponding `pytest` test, and `docs/midcourse/verification.md`
   records the pass/fail counts at each step.
2. **Manual browser verification** — a table in `verification.md` records
   hands-on checks of the frontend against the running backend, since no
   automated browser testing exists in this project.
3. **Break tests as documentation proof** — for two business rules
   (status-transition validation, duplicate-task detection), the
   implementation was deliberately broken, the expected test failure was
   captured verbatim, then reverted and reconfirmed passing. This is used
   as evidence that the documented rule is actually enforced by the test
   suite, not just asserted in prose.

## 3. Alternatives Considered

- **Doctest execution** (`pytest --doctest-modules` or similar) to actually
  run the `>>>` `Example` blocks added to `app/main.py` docstrings. Not
  currently wired into `pytest` or `ci.yml` [VERIFY — no `pytest.ini`,
  `pyproject.toml`, or `setup.cfg` pytest config was found in this repo, so
  no doctest collection is configured anywhere].
- **A documentation linter** (e.g., checking that README/CLAUDE.md command
  blocks match what CI actually runs) — not adopted; consistency between
  `CLAUDE.md`'s `pytest -v` / `uvicorn ...` commands and `ci.yml`'s
  `pytest -v --tb=short` is currently maintained by hand.
- **CI-driven manual-check replacement** (e.g., Playwright/Selenium smoke
  tests replacing the manual browser-check table) — not adopted; the
  manual table in `verification.md` remains the only record of frontend
  behavior checks.

## 4. Trade-offs

Not everything I documented is actually checked by a machine. The
Example blocks in the docstrings could go out of date and nothing would
warn me. The manual browser checks only prove the frontend worked at
that one moment, not that it still works later. The two break tests were
solid proof, but I did them by hand once — they don't run automatically
every time. I'd fix this by adding pytest --doctest-modules to CI so the
Example blocks actually get tested.

## 5. Consequences

- Anyone reading `docs/midcourse/verification.md` gets a concrete,
  evidence-based account of what was tested and how, rather than an
  unverified claim that "everything works."
- The break-test technique gives real confidence that the two rules it
  covers (status transitions, duplicate detection) are genuinely enforced
  by the test suite, not just present in code with no test actually
  exercising the failure path.
- Documentation drift risk remains for anything not covered by an
  automated test: the docstring `Example` blocks, the manual browser-check
  table, and the README/CLAUDE.md command instructions are all currently
  unverified by CI.
- No auth, database, deployment, or production-hardening claims are made
  anywhere in this documentation, consistent with `CLAUDE.md`'s do-not
  rules — this note does not introduce any either.

## 6. Open Questions

Is the manual browser-check table good enough, or should it be
automated? Is two break tests enough to trust the rest of the suite, or
should I test more rules the same way? Is it worth building a check that
makes sure README.md and CLAUDE.md match what CI actually runs, or is
that overkill for a project this small?