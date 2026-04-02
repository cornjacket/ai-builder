# Task: create-regression-test-dir

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | b9529c-doc-pipeline/b9529c-0009-doc-platform-monolith-regression-test             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Create the `tests/regression/doc-platform-monolith/` directory structure,
mirroring `doc-user-service/`.

## Context

Directories needed: `tests/regression/doc-platform-monolith/source/` (with the
full platform-monolith subdirectory tree: `cmd/platform/`, `internal/metrics/`,
`internal/metrics/handlers/`, `internal/metrics/store/`, `internal/iam/`,
`internal/iam/lifecycle/`, `internal/iam/authz/`), plus `gold/` and `runs/`.
Add a `./doc-platform-monolith/gold` entry to `tests/regression/go.work`.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
