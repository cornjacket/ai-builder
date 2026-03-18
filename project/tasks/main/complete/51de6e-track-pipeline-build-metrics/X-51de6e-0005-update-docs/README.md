# Task: update-docs

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

Update documentation to cover the new metrics system.

- `ai-builder/orchestrator/agent_wrapper.md` — document the new token fields
  in `AgentResult` and the `result` event parsing
- `ai-builder/orchestrator/metrics.md` (new) — document the metrics module:
  all functions, `InvocationRecord` / `RunData` dataclasses, and the
  `## Execution Log` section contract
- `ai-builder/orchestrator/orchestrator.md` — add section on metrics
  instrumentation: when `build_readme` is set, when writes happen
- `ai-builder/orchestrator/README.md` — add `metrics.py` to the file index

## Context

Every source file needs a companion .md per project convention. The metrics
module is new so it needs a fresh companion doc. The existing orchestrator
and agent_wrapper docs need updating to reflect new behaviour.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
