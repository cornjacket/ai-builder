# Task: update-supporting-scripts

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | c98d7b-incremental-subtask-ids             |
| Priority    | —           |

## Goal

Audit and update all supporting scripts to handle both the new incremental
naming convention and the `X-` prefix on completed subtask directories:

- `list-tasks.sh` — strip `X-` when displaying names; skip or mark `X-`
  prefixed entries as complete
- `show-task.sh` — resolve task by name with or without `X-` prefix
- `move-task.sh` — handle `X-` prefix during moves
- `delete-task.sh`, `restore-task.sh`, `wont-do-subtask.sh` — same

Scripts that look up a subtask directory by name must match both
`{id}-{name}` and `X-{id}-{name}` forms.

## Context

The `X-` rename in `complete-task.sh` changes the on-disk directory name.
Any script that locates a subtask by scanning a parent directory must be
updated to handle the new prefix, or lookups will break after the first
completion.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
