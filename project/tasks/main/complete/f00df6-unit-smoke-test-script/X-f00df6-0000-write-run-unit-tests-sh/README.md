# Task: write-run-unit-tests-sh

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

Write `tests/unit/run-unit-tests.sh` — the top-level script that runs
the full unit test suite locally and in CI.

## Context

The script is the single entry point for all unit tests. It must:
- Run Python tests via `pytest tests/unit/` (discovers existing unittest files)
- Run shell tests via `bats tests/unit/shell/` (if bats is installed and tests exist)
- Accept flags: `--python` (Python only), `--shell` (shell only), `--coverage` (add pytest-cov)
- Print a clear summary (pass/fail counts per suite)
- Exit 0 only if all suites pass; exit 1 on any failure
- Work from the repo root (no `cd` required) and from inside `tests/unit/`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
