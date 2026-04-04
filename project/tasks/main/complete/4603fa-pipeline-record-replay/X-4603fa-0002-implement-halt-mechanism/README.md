# Task: implement-halt-mechanism

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 4603fa-pipeline-record-replay             |
| Priority    | —           |
| Created     | 2026-04-02            |
| Completed | 2026-04-02 |
| Next-subtask-id | 0000               |

## Goal

Add `--halt-after-ai-invocation N` flag to orchestrator.py. When set, the orchestrator halts cleanly after the Nth AI role invocation (ARCHITECT, IMPLEMENTOR, TESTER — not handlers) and all subsequent non-AI handler steps for that cycle complete. At halt, current-job.txt is advanced to the next task, leaving the workspace in the same state as a natural crash between handler completion and the next AI call.

## Context

See brainstorm `sandbox/brainstorms/brainstorm-pipeline-stop-and-replay.md`, section "Halt Mechanism". This flag is independent of `--record-to` and is used for resume testing without requiring a real crash scenario.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
