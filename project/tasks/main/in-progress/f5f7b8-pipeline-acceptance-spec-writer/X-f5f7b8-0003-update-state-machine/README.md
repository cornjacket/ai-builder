# Task: update-state-machine

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | f5f7b8-pipeline-acceptance-spec-writer             |
| Priority    | —           |
| Created     | 2026-04-04            |
| Completed | 2026-04-04 |
| Next-subtask-id | 0000               |

## Goal

Add the `ACCEPTANCE_SPEC_WRITER` state to `machines/builder/default.json` so
it runs before the TOP ARCHITECT decompose step.

## Context

The new state must be inserted as the first step after the job doc is received,
before any ARCHITECT state. The transition from `ACCEPTANCE_SPEC_WRITER` goes
to the existing TOP ARCHITECT decompose state on success, or halts on error
(non-HTTP interface detected).

File to modify:
- `ai-builder/orchestrator/machines/builder/default.json`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
