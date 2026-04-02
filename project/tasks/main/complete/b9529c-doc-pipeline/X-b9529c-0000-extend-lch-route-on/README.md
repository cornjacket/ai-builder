# Task: extend-lch-route-on

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | b9529c-doc-pipeline             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Add a `route_on` config field to LCHAgent so it can emit different outcome tokens
based on a field read from the next task's `task.json`. The machine JSON declares
the mapping; LCH has no hardcoded pipeline knowledge.

## Context

Config shape (in machine JSON):

```json
"LEAF_COMPLETE_HANDLER": {
  "route_on": {
    "field": "component_type",
    "default": "HANDLER_SUBTASKS_READY",
    "integrate": "HANDLER_INTEGRATE_READY"
  }
}
```

If `component_type` is absent or its value doesn't match any listed key, emit
the `default` outcome. An explicit `default` key is required — no silent fallback.

LCH reads `route_on` from its role config (passed via `AgentContext` or machine
loader). The orchestrator/loader already passes the full role config dict to
internal agents; LCH just needs to consume it.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
