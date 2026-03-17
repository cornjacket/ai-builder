# Task: review-regression-test-readmes

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | regression-test, docs |
| Priority    | MED                   |

## Goal

Review all regression test READMEs under `tests/regression/` for correctness
and update any that are outdated. Each README should accurately reflect the
current run instructions, directory structure, sandbox paths, and expected
pipeline routing.

## Context

The regression tests have evolved alongside the pipeline. Known areas likely
to be stale:
- Sandbox paths (some may still reference `/tmp/`)
- Run commands (flags, script names)
- Directory structure listings
- Expected pipeline routing tables (outcomes were renamed, TM flow changed)
- `decomposition.md` reference in user-service README (still mentions old TM logic)

Tests to review: `fibonacci/`, `template-setup/`, `user-service/`.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
