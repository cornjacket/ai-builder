# Task: split-user-scripts

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 829461-split-task-format-md-json-and-scripts             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Verify and update user-facing task scripts so they correctly handle the new
two-file format (README.md prose + task.json metadata) for pipeline subtasks,
without leaking pipeline concerns into user-task scripts.

## Context

After subtask 0001, pipeline subtasks have task.json for structured metadata
and a prose-only README.md. User tasks still use README.md only (no task.json).

The user-facing scripts (`move-task.sh`, `list-tasks.sh`, `wont-do-subtask.sh`,
`delete-task.sh`, `show-task.sh`) were written when all tasks had a single
README with a metadata table. Some need updates:

- `move-task.sh`: updates `| Status |` in README via sed. For pipeline builds
  (which users do move, e.g., draft → in-progress before submitting), there is
  no metadata table, so the sed is a no-op. We need to also update task.json
  status if present.
- `list-tasks.sh`: reads Priority and Tags from README. These are absent for
  pipeline tasks, but the fallback to `—` already handles this gracefully.
  No change needed.
- `wont-do-subtask.sh`, `delete-task.sh`, `show-task.sh`: only operated on
  user tasks in practice. No change needed.
- `task-template.md`: legacy template with pipeline fields (Complexity,
  Stop-after, Last-task, Components, Design). Superseded by
  `user-task-template.md`, `user-subtask-template.md`, and
  `pipeline-build-template.md`. Must be removed.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
