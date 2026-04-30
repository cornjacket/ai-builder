# Task: test-category-flag

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | task-tooling           |
| Created     | 2026-04-30            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Living example of `new-user-task.sh --category` correct usage. This task was
created to verify the `--category` flag added under
[`4a8789-0000-add-category-flag-to-new-user-task`](../../in-progress/4a8789-investigate-task-partitioning-for-parallel-worktrees/4a8789-0000-add-category-flag-to-new-user-task/).

## Context

The task was created with:

```bash
project/tasks/scripts/new-user-task.sh \
    --epic main --folder draft \
    --name test-category-flag \
    --category task-tooling
```

The expected behaviour, all verified:

1. Omitting `--category` exits 1 with the updated usage banner.
2. `--category not-a-real-class` exits 1 and prints the valid values parsed
   from `project/tasks/classes.md` (plus `unclassified`).
3. A valid `--category` populates the `Category` field in this README,
   replacing the old hardcoded `—`.

Kept rather than deleted, per the CLAUDE.md rule that test tasks are living
examples of correct usage.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
