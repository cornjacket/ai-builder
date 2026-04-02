# Task: copy-platform-monolith-source-as-template

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

Populate `tests/regression/doc-platform-monolith/source/` with the Go source
files from `sandbox/platform-monolith-output/`, retaining two pre-existing
`.md` files to simulate a partial-documentation scenario.

## Context

Copy all `.go` files (preserving subdirectory structure) from
`sandbox/platform-monolith-output/` plus `go.mod` and `go.sum`.

**Retain these `.md` files in the template** (do NOT strip them):
- `internal/iam/README.md`
- `internal/metrics/README.md`

Strip all other `.md` files (e.g. `master-index.md`). Also copy `doc-spec.md`
from `doc-user-service/doc-spec.md` and adapt it for the platform-monolith.

Add a sanity check to `reset.sh` (in the next subtask) that verifies these
two `.md` files are present in the template before proceeding — they must not
be accidentally stripped.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
