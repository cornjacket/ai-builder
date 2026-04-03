# Task: unit-smoke-test-script

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Priority    | HIGH           |
| Created     | 2026-04-02            |
| Completed | 2026-04-02 |
| Next-subtask-id | 0006 |

## Goal

Implement a full unit test cycle script that runs a broad smoke test across the
ai-builder codebase after a feature has been implemented and unit tested. The
script must work locally (e.g. after a `git merge` from a feature branch) and
in CI in the cloud.

## Context

Currently there is no automated sweep that validates the whole codebase after a
feature lands. Each pipeline stage (TESTER) validates its own output, but
nothing catches cross-cutting regressions introduced by a merge. This task
closes that gap.

**Intended use cases:**
- Developer runs the script locally after merging a feature branch into `main`
  to confirm nothing is broken before pushing.
- CI runs the same script on every push/PR to `main` (and optionally on feature
  branches).

**Scope of "unit smoke test":**
- All Python unit tests in `ai-builder/` (orchestrator, task scripts, utilities)
- Any shell script self-tests / bats tests if they exist
- Should be fast enough to run on every commit — not a full regression pipeline
  run (that requires live LLM calls and is expensive)

**Out of scope:**
- Full end-to-end pipeline regression (handled separately by regression tests)
- Target-repo compilation or integration tests

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-f00df6-0000-write-run-unit-tests-sh](X-f00df6-0000-write-run-unit-tests-sh/)
- [x] [X-f00df6-0001-add-pytest-infrastructure](X-f00df6-0001-add-pytest-infrastructure/)
- [x] [X-f00df6-0002-python-tests-render-and-index](X-f00df6-0002-python-tests-render-and-index/)
- [x] [X-f00df6-0003-shell-tests-bats-task-scripts](X-f00df6-0003-shell-tests-bats-task-scripts/)
- [x] [X-f00df6-0004-fix-sed-portability](X-f00df6-0004-fix-sed-portability/)
- [x] [X-f00df6-0005-github-actions-ci-workflow](X-f00df6-0005-github-actions-ci-workflow/)
<!-- subtask-list-end -->

## Notes

- Script lives at `tests/unit/run-unit-tests.sh`. Flags: `--python`, `--shell`, `--coverage`.
- Python runner: pytest (runs existing unittest tests natively). Dev deps in `requirements-dev.txt`.
- Shell runner: bats-core. Shell tests live in `tests/unit/shell/`.
- CI: GitHub Actions, `.github/workflows/unit-tests.yml`, triggers on push/PR to main.
- The script must exit non-zero on any test failure so CI can gate on it.
- `orchestrator.py` (1,177 lines, zero tests) is NOT in scope — it requires
  refactoring before it is unit-testable. Treat as a follow-on HIGH task.
- Coverage: report only at first; introduce a gating threshold once a baseline exists.

**Brainstorm:** `sandbox/brainstorms/brainstorm-unit-smoke-test-script.md`
