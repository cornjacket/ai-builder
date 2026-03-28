# Task: resume-execution-log-continuity

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 49352f-redesign-pipeline-communication-architecture             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

On `--resume`, pre-populate `run.invocations` from the existing
`execution_log` in the TOP-level `task.json` so that the resumed run's
invocations append to the stalled run's rather than replacing them. Insert a
sentinel `RESUME` entry into the log at the join point so the history is
auditable.

## Context

`run = RunData(...)` always starts empty. On resume the first
`write_metrics_to_task_json` call overwrites the previous `execution_log`,
losing the stalled run's data.

**Fix:**
At orchestrator startup, when `--resume` (or `--clean-resume`) is set and
`top_task_json` is resolvable, read the existing `execution_log` array from
`task.json` and reconstruct `InvocationRecord` objects from it to seed
`run.invocations`. Then append a synthetic sentinel entry:

```
role:        "RESUME"
agent:       "orchestrator"
description: "pipeline resumed"
outcome:     "RESUME"
tokens_in/out/cached: 0
elapsed_s:   0
```

This means all subsequent invocations appear after the sentinel in a single
continuous log. The `run.start` should be set to the original run's start
time (taken from the first entry in the existing log) so elapsed totals in
`run_summary` are meaningful.

`top_task_json` may not be known at startup if `--job` is omitted on resume
(the orchestrator derives it from `current-job.txt`). Seed the log as soon as
`top_task_json` is first resolved — the same lazy-resolution path already used
for incremental metrics writes.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
