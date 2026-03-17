# Task: update-documentation

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | c98d7b-incremental-subtask-ids             |
| Priority    | —           |

## Goal

Update all documentation to reflect the new naming convention:

- `CLAUDE.md` — update task management rules; update the scripts reference
  section to mention `Next-subtask-id`; update example task names
- `project/tasks/README.md` — update naming convention description and
  any examples showing subtask directory names
- `target/CLAUDE.md` — same as above for the target copy

## Context

CLAUDE.md is loaded at the start of every session. If it still describes
the old random-hash convention, the AI will produce subtasks in the wrong
format. This subtask ensures the docs match the implementation before the
task is closed.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
