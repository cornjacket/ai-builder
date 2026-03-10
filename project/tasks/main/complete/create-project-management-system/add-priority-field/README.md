# Task: add-priority-field

| Field    | Value                            |
|----------|----------------------------------|
| Status   | complete             |
| Epic     | main                             |
| Tags     | project-management, tooling      |
| Parent   | create-project-management-system |
| Priority | HIGH                             |

## Description

Add a `Priority` field to the task README template and surface it in
`list-tasks.sh` output.

- Add `| Priority | — |` to `task-template.md` (default `—`, valid values:
  `CRITICAL`, `HIGH`, `MED`, `LOW`).
- Update `new-task.sh` to accept an optional `--priority` flag (default `—`)
  and substitute `{{PRIORITY}}` in the template.
- Update `list-tasks.sh` to read the `Priority` field from each task's
  README and display it alongside the task name (e.g. `my-task [HIGH]`).

Priority is kept in the README metadata, not the directory name, so changing
priority never requires renaming a directory.

## Documentation

Update `project/tasks/README.md`: task format section (new Priority field),
scripts section (`new-task.sh --priority` flag).

## Subtasks

<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
