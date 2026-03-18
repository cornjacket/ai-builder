# Task: smoke-test

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 51de6e-track-pipeline-build-metrics             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Run the user-service regression test end-to-end and verify all metrics outputs
are correct.

Checks:
1. The top-level pipeline-subtask README (integrate, Level: TOP) has a populated
   `## Execution Log` table with one row per agent invocation after the run.
2. `sandbox/user-service-output/run-summary.md` exists and contains:
   - Header block with task name, start, end, total time
   - Per-invocation table (all invocations present, elapsed non-zero for all but first)
   - Per-role totals table
   - Token usage table with non-zero values and grand total row
3. `sandbox/user-service-output/run-metrics.json` exists and is valid JSON
   with the same data.
4. Gold tests still pass (8/8).

## Context

This is the gate check before closing the task. Reset with
`tests/regression/user-service/reset.sh`, run the pipeline, then inspect
the outputs manually before marking done.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
