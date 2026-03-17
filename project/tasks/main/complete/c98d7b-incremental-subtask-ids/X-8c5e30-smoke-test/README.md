# Task: smoke-test

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | c98d7b-incremental-subtask-ids             |
| Priority    | —           |

## Goal

Manually verify the new system end-to-end against a scratch task:

1. Create a test user-task in `draft/`
2. Add three subtasks — confirm they are named `{id}-0000-*`, `{id}-0001-*`,
   `{id}-0002-*` and that `Next-subtask-id` increments correctly in the parent
3. Mark the first subtask complete — confirm the directory is renamed to
   `X-{id}-0000-*` and the parent subtask list shows `[x]`
4. Run `list-tasks.sh` — confirm output is readable and `X-` entries display
   correctly
5. Delete the scratch task when done

Document any discrepancies found and fix before marking this subtask complete.

## Context

This is the gate check before the task is closed. All scripts must work
together correctly — creation, completion, and listing — for the system to
be considered done.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
