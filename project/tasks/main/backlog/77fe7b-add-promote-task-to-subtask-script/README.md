# Task: add-promote-task-to-subtask-script

| Field    | Value                |
|----------|----------------------|
| Status   | backlog           |
| Epic     | main             |
| Tags     | task-management, scripts             |
| Parent   | —           |
| Priority | MED         |

## Description

Add a `promote-to-subtask.sh` script that moves an existing top-level task
into another task as a subtask. This operation currently has no script,
forcing manual directory moves and README edits which is error-prone.

**Behaviour:**
```
promote-to-subtask.sh --epic main --folder draft --name <task> \
    --parent-folder <status> --parent <parent-task>
```

1. Move the task directory into the parent task directory
2. Update the task README `Parent` field to the new parent
3. Update the parent README subtask list to include the new subtask
4. Update the epic folder `README.md` to remove the old top-level entry

**Also update:**
- `project/tasks/README.md` — add script to the scripts table and usage examples
- `target/project/tasks/README.md` — same
- `CLAUDE.md` — add rule: use `promote-to-subtask.sh` when a task needs to
  become a subtask of another; never manually move task directories

## Documentation

Update both `project/tasks/README.md` and `target/project/tasks/README.md`
with the new script, and `CLAUDE.md` with the rule.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
