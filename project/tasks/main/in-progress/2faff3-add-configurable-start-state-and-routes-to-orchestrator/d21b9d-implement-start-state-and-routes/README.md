# Task: implement-state-machine

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | PIPELINE-SUBTASK       |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 2faff3-add-configurable-start-state-and-routes-to-orchestrator             |
| Priority    | —           |
| Complexity  | —                      |
| Stop-after  | false                  |
| Last-task   | false                  |
| Level       | INTERNAL              |

## Goal

Implement the `--state-machine` flag and the accompanying JSON machine
file format, plus `--start-state` as a runtime override.

## Context

Scope expanded from original `--start-state` + `--routes` design during
brainstorm (`82c090`). The full design:

**`--state-machine <file.json>`** — loads a complete machine definition:
- `start_state` — the default entry role
- `roles` — agent assignment and prompt file path per role
- `transitions` — the full state diagram (replaces hardcoded `ROUTES`)

**`--start-state <ROLE>`** — runtime override of `start_state` from the
machine file; useful for testing and resuming at a specific role.

Both flags are optional; existing hardcoded behaviour is the fallback.
The default machine ships as a committed file at
`ai-builder/orchestrator/machines/default.json`.

Prompt files in the machine use `null` for roles with dynamic/generated
prompts (currently `DECOMPOSE_HANDLER` and `LEAF_COMPLETE_HANDLER`);
the orchestrator falls back to built-in generation for those.

Depends on `d05f90-split-task-manager-into-handlers` completing first.

## Components

_To be completed by the ARCHITECT._

## Design

_To be completed by the ARCHITECT._

## Acceptance Criteria

_To be completed by the ARCHITECT._

## Suggested Tools

_To be completed by the ARCHITECT._

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
