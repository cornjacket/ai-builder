# Task: update-templates

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | c98d7b-incremental-subtask-ids             |
| Priority    | —           |

## Goal

Add `Next-subtask-id: 0000` to the metadata table in all three task
templates and their target copies:

- `project/tasks/TASK-TEMPLATE.md`
- `project/tasks/USER-SUBTASK-TEMPLATE.md`
- `project/tasks/PIPELINE-SUBTASK-TEMPLATE.md`
- `target/project/tasks/TASK-TEMPLATE.md`
- `target/project/tasks/USER-SUBTASK-TEMPLATE.md`
- `target/project/tasks/PIPELINE-SUBTASK-TEMPLATE.md`

The field appears after `Priority` in the metadata table and is always
initialized to `0000`.

## Context

Templates are the source of truth for newly created task READMEs. Adding
the field here ensures every task created after this change automatically
has `Next-subtask-id` ready for the scripts to read and increment.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
