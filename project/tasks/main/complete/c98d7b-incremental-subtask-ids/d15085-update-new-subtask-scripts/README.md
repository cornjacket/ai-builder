# Task: update-new-subtask-scripts

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | c98d7b-incremental-subtask-ids             |
| Priority    | —           |

## Goal

Update `new-user-subtask.sh` and `new-pipeline-subtask.sh` to use
incremental IDs instead of random hashes:

1. Read `Next-subtask-id` from the parent's README metadata table
2. Derive the parent's short ID from its directory name (everything before
   the first `-` that is followed by a non-numeric character — i.e. the
   6-char hex prefix of the parent directory)
3. Name the new subtask directory `{parent-short-id}-{next-id}-{name}`
   (e.g. `c98d7b-0003-update-complete-script`)
4. Increment `Next-subtask-id` in the parent README after creation

Write a shared helper (`task-id-helpers.sh` or inline functions) for the
read/increment/write steps so both scripts stay DRY.

## Context

Currently both scripts call `openssl rand -hex 3` (or similar) to generate
a random prefix. That logic is replaced by reading a counter from the parent
README. The parent README field is the single source of truth for the next
available ID.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
