# Task: update-tm-acronym-references

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

Audit all documentation, task files, and code for residual "TM" acronym usage
and update each reference to use the correct term for its context.

## Context

The `TASK_MANAGER` role was split into `DECOMPOSE_HANDLER` and
`LEAF_COMPLETE_HANDLER` in `d05f90`. While the orchestrator source and its
companion docs (`orchestrator.md`, `routing.md`, `pipeline-behavior.md`) were
updated as part of that subtask, "TM" and "TASK_MANAGER" may still appear in:
task READMEs, backlog tasks (e.g. `a09648-optimize-pipeline-tm-prompt`), the
brainstorm doc, other docs under `ai-builder/`, and comments. Each occurrence
should be updated to the precise term it represents — `DECOMPOSE_HANDLER`,
`LEAF_COMPLETE_HANDLER`, "handler", or "pipeline handler" as appropriate.
Generic uses of "TM mode" (meaning the `--target-repo` pipeline mode) should
be replaced with "TM mode" only where no better term exists, or renamed to
"pipeline mode" for clarity.

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
