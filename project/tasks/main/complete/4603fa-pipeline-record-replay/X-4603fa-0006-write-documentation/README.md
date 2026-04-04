# Task: write-documentation

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 4603fa-pipeline-record-replay             |
| Priority    | —           |
| Created     | 2026-04-02            |
| Completed | 2026-04-03 |
| Next-subtask-id | 0000               |

## Goal

Write user-facing documentation for the record/replay feature. Cover:
- How to capture a recording (`--record-to`)
- How to replay (`--replay-from`)
- How to halt at N AI invocations (`--halt-after-ai-invocation`)
- How to compare a recording snapshot against the output directory
- How prompt drift detection works and what to do when it triggers
- The `recording.json` manifest format

Documentation should live alongside the orchestrator (e.g. `ai-builder/orchestrator/record-replay.md`) and be linked from the orchestrator README.

## Context

Depends on all implementation subtasks (0001–0005) being complete.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
