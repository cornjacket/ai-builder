# Task: review-handoff-accumulation-mechanism

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 3fa24b-bug-handler-prompt-inefficiency             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Review whether the accumulated handoff history mechanism is appropriate for all role types
and redesign scoping so each role receives only the context it actually needs.

## Context

Currently `build_prompt()` appends ALL prior agent handoffs to every prompt, regardless
of role. This compounds with every invocation — by invocation 20 in the platform-monolith
run the accumulated context was 550k+ cached tokens even for a handler that runs one script.

The question is not just "handlers don't need this" (the immediate fix is in the parent
task) but whether the mechanism is right for creative roles too:
- Does IMPLEMENTOR need handoffs from 10 invocations ago, or just ARCHITECT's most recent?
- Does ARCHITECT need all prior context, or just the current job doc + immediately prior summary?
- Does TESTER need any handoff history, or only the current job doc?

Proposed scoping models to evaluate:
- **Handlers**: zero handoff history
- **TESTER**: zero handoff history (job doc is sufficient)
- **IMPLEMENTOR**: only the immediately preceding ARCHITECT handoff
- **ARCHITECT**: only the immediately preceding handoff (or none — the job doc IS the design record)

Also evaluate whether the growing context hurts quality (distraction, contradictions from
stale prior decisions) in addition to cost.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
