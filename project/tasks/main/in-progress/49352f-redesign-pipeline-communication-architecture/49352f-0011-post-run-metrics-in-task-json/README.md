# Task: post-run-metrics-in-task-json

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 49352f-redesign-pipeline-communication-architecture             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

After `HANDLER_ALL_DONE`, write run metrics and the execution log directly into
the TOP-level `task.json` as structured fields. Remove any separate
`run-metrics.json` or `run-summary.md` files.

## Context

Run metrics are currently written to a separate `run-metrics.json` file.
Under the JSON-native model, `task.json` is the single source of truth for all
pipeline state — metrics belong there, not in a sidecar file.

**Fields written to TOP-level `task.json`:**
```json
{
  "run_summary": {
    "start": "2026-03-24T23:42:09Z",
    "end": "2026-03-24T23:55:00Z",
    "total_tokens_in": 245000,
    "total_tokens_out": 18000,
    "total_tokens_cached": 120000,
    "invocation_count": 12
  },
  "execution_log": [
    {
      "role": "ARCHITECT",
      "agent": "gemini",
      "outcome": "ARCHITECT_DECOMPOSITION_READY",
      "tokens_in": 21000,
      "tokens_out": 1800,
      "tokens_cached": 8000,
      "timestamp": "2026-03-24T23:42:09Z"
    }
  ]
}
```

The execution log accumulates one entry per agent invocation throughout the run.
The orchestrator appends to it after each stage, not only at the end.
`run_summary` totals are computed and written on `HANDLER_ALL_DONE`.

The README render (subtask 0012) reads these fields from `task.json` to produce
the human-readable execution log table.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
