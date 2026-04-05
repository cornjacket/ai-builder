# Task: enforce-task-close-before-commit

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | bootstrap              |
| Created     | 2026-04-05            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Establish and enforce a rule that tasks must be closed (moved to `complete/`)
before the final commit for that task is made. Currently tasks are left in
`in-progress/` after implementation is done and only closed later — or not at
all — which makes the task list misleading.

Changes required:
- Update `CLAUDE.md` to state the rule explicitly: close the task with
  `complete-task.sh` before (or as part of) the final commit
- Update the commit guidelines in `CLAUDE.md` to include task closure as a
  pre-commit step when finishing a task
- Consider whether `new-workflow.sh` or a pre-commit hook can enforce this
  automatically (research and decide as part of this task)

## Context

After implementing `4d6757-harden-worktree-scripts` and
`e7b46d-require-task-complete-before-worktree-removal`, both tasks were left
in `in-progress/` despite all subtasks being done, and committed in that state.
The user had to ask explicitly to close them. The workflow should make closing
the task a natural final step, not an afterthought.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
