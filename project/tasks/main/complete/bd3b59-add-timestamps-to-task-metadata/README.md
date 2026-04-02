# Task: add-timestamps-to-task-metadata

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Next-subtask-id | 0000               |
## Goal

Add `Created` and `Completed` timestamp fields to task metadata so the age
and completion time of work can be tracked at a glance.

## Context

Task metadata currently has no timestamps, making it impossible to tell when
a task was created or finished without reading git history. Adding `Created`
and `Completed` fields enables at-a-glance chronological context — useful for
session continuity, audit trails, and understanding pipeline velocity.

No `Updated` field — the only meaningful event after creation is completion.

**Scope by task type:**

| Task type | Created | Completed | 2026-04-02 |
|---|---|---|---|
| USER-TASK | yes | yes | README metadata table |
| USER-SUBTASK | yes | yes | README metadata table |
| PIPELINE-SUBTASK | yes | yes | `task.json` (README is prose-only) |

**Changes required:**
- `user-task-template.md` — add `Created` and `Completed` rows
- `user-subtask-template.md` — add `Created` and `Completed` rows
- `new-user-task.sh` — populate `Created` at creation (ISO 8601 date)
- `new-user-subtask.sh` — populate `Created` at creation
- `new-pipeline-subtask.sh` — add `created_at` to `task.json`
- `complete-task.sh` — set `Completed` in README (user tasks/subtasks) and `completed_at` in `task.json` (pipeline subtasks)
- `project/tasks/README.md` — document the new fields
- No backfill of existing tasks — git log is authoritative for those

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
