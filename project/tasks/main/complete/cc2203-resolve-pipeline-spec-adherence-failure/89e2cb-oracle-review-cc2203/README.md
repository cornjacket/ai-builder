# Task: oracle-review-cc2203

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | review           |
| Parent      | cc2203-resolve-pipeline-spec-adherence-failure             |
| Priority    | HIGH             |

## Goal

Oracle reviews all changes delivered under cc2203 before the task is
closed and committed.

## Context

cc2203 fixed two root causes of the platform-monolith spec adherence
failure:

1. **ARCHITECT.md contract propagation** — decompose mode now requires
   full API contract (routes + parameter models) for HTTP-handling
   components, data models only for internal components.

2. **Platform-monolith spec** — reset.sh heredoc corrected from
   "two independent processes" to a networked monolith (one binary,
   one process, two listeners, `cmd/platform/main.go`).

3. **Gold test fixes** — `gold_test.go` updated to look for
   `cmd/platform/` specifically, scan `outputDir` (not target repo),
   and call `cmd.Wait()` after kill to avoid I/O timeout.

4. **Third pipeline run** — all 17 gold tests pass.

Key files to review:
- `roles/ARCHITECT.md` — contract propagation rules
- `tests/regression/platform-monolith/reset.sh` — updated spec
- `tests/regression/platform-monolith/gold/gold_test.go` — gold test fixes

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
