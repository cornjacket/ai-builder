# Task: add-rename-and-insert-subtask-scripts

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Add two task management scripts:
- `rename-subtask.sh` — rename a subtask (change its NNNN ID and directory name)
- `insert-subtask.sh` — insert a new subtask at a given position, shifting existing subtasks up

## Context

Currently there is no way to rename or reorder subtasks without manually renaming
directories and editing the parent README's subtask-list. This came up when adding
a new subtask between 0002 and 0003 — required manually renaming 0003→0004 and
0004→0005, updating the parent README, updating internal README references, and
creating the new 0003 by hand. Error-prone and tedious.

**`rename-subtask.sh`**

Rename a subtask from one NNNN ID to another:
- Rename the directory (`e62647-NNNN-name` → `e62647-MMMM-name`)
- Update the `<!-- subtask-list -->` entry in the parent README
- Update `Next-subtask-id` in the parent if necessary

Usage:
```bash
rename-subtask.sh --epic main --folder in-progress --parent <task> --name <subtask> --new-id NNNN
```

**`insert-subtask.sh`**

Insert a new subtask at a given position, shifting all subsequent subtasks up by one:
- Rename all subtasks from position N onward (N→N+1, N+1→N+2, etc.)
- Create the new subtask at position N using the standard template
- Update the parent README's subtask-list and `Next-subtask-id`

Usage:
```bash
insert-subtask.sh --epic main --folder in-progress --parent <task> --at NNNN --name <name>
```

Both scripts should be mirrored to `target/project/tasks/scripts/` following the
same pattern as other scripts.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
