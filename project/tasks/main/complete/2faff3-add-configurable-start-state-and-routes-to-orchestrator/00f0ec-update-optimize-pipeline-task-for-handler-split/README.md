# Task: update-optimize-pipeline-task-for-handler-split

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 2faff3-add-configurable-start-state-and-routes-to-orchestrator             |
| Priority    | —           |

## Goal

Update `a09648-optimize-pipeline-tm-prompt` in the backlog to reflect
the TASK_MANAGER split into `DECOMPOSE_HANDLER` and `LEAF_COMPLETE_HANDLER`.

## Context

`a09648` was written when TASK_MANAGER was a single role with two
branches ("Branch A" and "Branch B"). After `d05f90-split-task-manager-into-handlers`
is complete, that framing is obsolete. The task title, tags, goal,
context, and analysis notes all reference "TM" and the two-branch
structure. They need to be rewritten to reference the two new roles
by name and reflect that the branching problem has already been solved
by the split.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
