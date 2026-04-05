# Task: require-task-complete-before-worktree-removal

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | in-progress             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | bootstrap              |
| Created     | 2026-04-05            |
| Completed   | —                      |
| Next-subtask-id | 0002 |

## Goal

`remove-worktree.sh` must verify that the worktree's associated task and all its
subtasks are complete before allowing deletion. This prevents silently losing task
context when a worktree is removed.

The script must:
1. Derive the associated task from the worktree/branch name — by convention the
   branch name matches the task name (e.g. branch `establish-regression-recordings`
   → task `ccf4a4-establish-regression-recordings`).
2. Locate the task in the task tree (`project/tasks/<epic>/`).
3. Check that the task's `Status` is `complete` (i.e. it is in the `complete/` folder).
4. Check that all subtasks are marked done (`[x]` prefix or `X-` directory prefix).
5. If any check fails, print a clear message listing the incomplete items and refuse
   deletion.

## Context

Worktree branches are named after their task (e.g. `establish-regression-recordings`
for `ccf4a4-establish-regression-recordings`). The hex prefix is not part of the
branch name, so the script must search by suffix match across all task folders.

Deleting a worktree without completing its task leaves the task tree in a misleading
state — the worktree is gone but the task appears in-progress indefinitely.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-e7b46d-0000-add-task-completion-check-to-remove-worktree](X-e7b46d-0000-add-task-completion-check-to-remove-worktree/)
- [x] [X-e7b46d-0001-update-docs](X-e7b46d-0001-update-docs/)
<!-- subtask-list-end -->

## Notes

_None._
