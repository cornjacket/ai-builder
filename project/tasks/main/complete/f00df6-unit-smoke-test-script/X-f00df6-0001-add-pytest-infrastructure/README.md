# Task: add-pytest-infrastructure

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | f00df6-unit-smoke-test-script             |
| Priority    | —           |
| Created     | 2026-04-02            |
| Completed | 2026-04-02 |
| Next-subtask-id | 0000               |

## Goal

Add pytest as the Python test runner and create shared test fixtures in
`conftest.py`.

## Context

Currently tests use Python `unittest` with manual `sys.path.insert()` hacks
and repeated boilerplate for temp dirs. Pytest runs unittest tests natively,
so no rewrites are needed — but adding pytest unlocks fixtures, parameterize,
and coverage reporting.

Deliverables:
- `requirements-dev.txt` — `pytest`, `pytest-cov`
- `tests/unit/conftest.py` — shared fixtures: `tmp_task_dir` (creates a
  minimal task directory tree in a temp dir), `mock_task_json` (builds a
  task.json dict with sensible defaults)
- Verify all three existing test files pass under `pytest`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
