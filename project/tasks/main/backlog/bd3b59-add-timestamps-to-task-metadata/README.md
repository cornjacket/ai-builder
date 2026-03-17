# Task: add-timestamps-to-task-metadata

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |

## Goal

Add `Created` and `Updated` timestamp fields to the metadata table of all
USER-TASK, USER-SUBTASK, and PIPELINE-SUBTASK READMEs so that the history
of when work was created and last modified can be tracked.

## Context

Task READMEs currently have no timestamp fields, making it impossible to
tell when a task was created or last changed without reading git history.
Adding `Created` and `Updated` fields to the metadata table enables at-a-glance
chronological context — useful for session continuity, audit trails, and
understanding pipeline velocity.

**Scope:**
- Update `new-user-task.sh`, `new-user-subtask.sh`, and
  `new-pipeline-subtask.sh` to populate `Created` at task creation time
  (ISO 8601 date, e.g. `2026-03-16`)
- Update `complete-task.sh` and any other mutation scripts (e.g.
  `move-task.sh`) to set `Updated` when the task's status changes
- Update the task README template embedded in each script
- Update `project/tasks/README.md` to document the new fields
- Decide whether to backfill existing tasks (likely not — too noisy,
  and git log is the authoritative source for existing tasks)

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
