# Task: migrate-existing-subtask-ids

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | c98d7b-incremental-subtask-ids             |
| Priority    | —           |

## Goal

Review all incomplete tasks (draft, backlog, in-progress) and recreate
their subtasks using the new `0000`-based incremental naming convention.
Completed tasks in `complete/` are left as-is — they are historical record.

For each incomplete task with subtasks:
1. Identify the subtask ordering (by creation order or logical sequence)
2. Rename subtask directories from `{hash}-{name}` to `{parent-id}-{NNNN}-{name}`
3. Add `X-` prefix to any already-complete subtasks
4. Update the parent README subtask list links to match the new names
5. Set `Next-subtask-id` in the parent README to the next available value

This is a one-time migration. After this subtask is complete, all active
tasks use the new scheme.

## Context

The new scripts only apply the incremental convention going forward. Existing
tasks created before this change still have random-hash subtask names. This
subtask bridges the gap so the full task tree is consistent.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
