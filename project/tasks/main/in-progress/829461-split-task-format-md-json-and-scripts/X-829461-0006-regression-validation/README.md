# Task: regression-validation

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 829461-split-task-format-md-json-and-scripts             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Run regression tests to validate the task.json split and internal
DECOMPOSE_HANDLER changes: fibonacci (non-TM, baseline), user-service
(TM, single decomposition level), and platform-monolith (TM, multi-level).

## Context

All pipeline subtasks now use task.json for structured metadata and prose-only
README.md. DECOMPOSE_HANDLER is now an internal Python function (zero AI
tokens). The regression validates:

1. **Fibonacci** (non-TM, simple.json): still works; no TM changes affect it
2. **User-service** (TM, default.json): single decomposition; validates that
   DECOMPOSE_HANDLER internal correctly parses the Components table, creates
   subtasks, fills Goal/Context, sets complexity/last-task/level in task.json
3. **Platform-monolith** (TM, default.json): multi-level decomposition;
   validates that the internal DECOMPOSE_HANDLER handles INTERNAL-level
   composite components correctly

Expected: all gold tests pass. Token usage for platform-monolith should be
≤ run 11 baseline (DECOMPOSE_HANDLER was already internal before run 11,
but this validates the full stack end-to-end).

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
