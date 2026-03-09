# Task: nice-to-have-enhancements

| Field  | Value                |
|--------|----------------------|
| Status | complete             |
| Epic   | main             |
| Tags   | project-management, tooling             |
| Parent | create-project-management-system           |

## Description

Quality-of-life improvements to the task management scripts that are useful
but not blocking:

- ~~**`complete-task.sh`**~~ — implemented. Unified script handles both
  top-level tasks (moves to `complete/`) and subtasks (checkbox + Status
  field), with `--undo` support. `complete-subtask.sh` is superseded.
- ~~**Search by tag**~~ — implemented. `list-tasks.sh --tag <tag>` filters
  to tasks whose Tags field contains the given value (case-insensitive).
- ~~**`show-task.sh`**~~ — implemented. Prints a task's README to stdout.

## Documentation

Update `project/tasks/README.md` scripts section when any of these are implemented.

## Subtasks

<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
