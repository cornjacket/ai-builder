# Task: add-task-manipulation-scripts

| Field    | Value                |
|----------|----------------------|
| Status   | draft           |
| Epic     | main             |
| Tags     | tooling, task-management             |
| Parent   | —           |
| Priority | MED         |

## Description

Add three structural manipulation scripts to the task management system.
These are needed by the TM during multi-level decomposition — as the
ARCHITECT decomposes composite components, the TM needs to restructure
the task tree to reflect the emerging hierarchy.

**Scripts to add:**

`rename-task.sh` — rename a task or subtask directory and update all
references (parent README checkbox, status README listing).
```bash
rename-task.sh --epic main --folder draft --name old-name --to new-name
rename-task.sh --epic main --folder draft --parent task-name --name old-subtask --to new-subtask
```

`convert-task.sh` — convert a top-level task into a subtask of another
task. Moves the directory, updates status README and the new parent's
subtask list.
```bash
convert-task.sh --epic main --folder draft --name task-name --parent new-parent
```

`promote-task.sh` — promote a subtask to a top-level task. Moves the
directory out of its parent into the status folder, removes the checkbox
from the parent README.
```bash
promote-task.sh --epic main --folder draft --parent parent-name --name subtask-name
```

All three scripts must:
- Keep the filesystem and READMEs in sync (same contract as existing scripts)
- Be idempotent where possible
- Be added to both `project/tasks/scripts/` and `target/project/tasks/scripts/`
- Be covered by the template-setup regression test

## Documentation

Add all three scripts to `project/tasks/README.md`, `target/project/tasks/README.md`,
and `CLAUDE.md` scripts reference section.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [ ] [674af4-implement-rename-task](674af4-implement-rename-task/)
- [ ] [7fdec0-implement-convert-task](7fdec0-implement-convert-task/)
- [ ] [c0ee85-implement-promote-task](c0ee85-implement-promote-task/)
<!-- subtask-list-end -->

## Notes

These scripts are needed by the TM during multi-level decomposition. When
the ARCHITECT marks a component as `composite`, the TM decomposes it further
and may need to restructure the task tree — promoting a subtask to a task,
converting a task to a subtask of a newly discovered parent, or renaming
nodes to match the ARCHITECT's terminology.

Also needed by humans during plan review — the human may want to restructure
the task tree produced by the Planning phase before approving it.
