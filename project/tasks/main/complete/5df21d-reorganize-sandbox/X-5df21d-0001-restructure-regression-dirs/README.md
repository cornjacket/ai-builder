# Task: restructure-regression-dirs

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 5df21d-reorganize-sandbox             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Move each regression's `sandbox/{name}-output/` and `sandbox/{name}-target/`
directories into `sandbox/regressions/{name}/output/` and
`sandbox/regressions/{name}/target/`.

## Context

Regressions to move:
- `doc-user-service`
- `doc-platform-monolith`
- `platform-monolith`
- `user-service`

Also move any other `sandbox/*-output/` and `sandbox/*-target/` pairs that exist
(e.g. `orchestrator`, `fibonacci`).

After moving, update every path reference in `tests/regression/`:
- `reset.sh` — TARGET_REPO and OUTPUT_DIR variables
- `run.sh` — TARGET_REPO and OUTPUT_DIR variables

Also check `CLAUDE.md` and any other files that reference the old sandbox paths
and update them.

Verify by running `tests/regression/doc-user-service/reset.sh` (dry-run check)
to confirm the paths resolve correctly.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
