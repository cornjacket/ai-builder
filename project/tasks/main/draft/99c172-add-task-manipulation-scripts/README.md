# Task: add-task-manipulation-scripts

| Field    | Value                        |
|----------|------------------------------|
| Status   | draft                        |
| Epic     | main                         |
| Tags     | tooling, task-management     |
| Parent   | —                            |
| Priority | MED                          |
| Category    | task-tooling           |
| Next-subtask-id | 0003               |
## Description

Add three structural manipulation scripts to the task management system
for use by humans when restructuring the task tree.

**Scripts to add:**

`rename-task.sh` — rename a task or subtask directory and update all
references (parent README checkbox, status README listing).
```bash
rename-task.sh --epic main --folder draft --name old-name --to new-name
rename-task.sh --epic main --folder draft --parent task-name --name old-subtask --to new-subtask
```

`promote-to-subtask.sh` — move a top-level task into another task as a
subtask. Moves the directory, removes it from the status README, adds it
to the new parent's subtask list, and updates the task's Parent field.
```bash
promote-to-subtask.sh --epic main --folder draft --name task-name --parent new-parent
```

`promote-to-task.sh` — promote a subtask to a top-level task. Moves the
directory out of its parent into the status folder, removes the checkbox
from the parent README, and clears the Parent field.
```bash
promote-to-task.sh --epic main --folder draft --parent parent-name --name subtask-name
```

All three scripts must:
- Keep the filesystem and READMEs in sync (same contract as existing scripts)
- Be added to both `project/tasks/scripts/` and `target/project/tasks/scripts/`
- Be covered by the template-setup regression test

## Documentation

Add all three scripts to `project/tasks/README.md`, `target/project/tasks/README.md`,
and the `CLAUDE.md` scripts reference section.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [ ] [99c172-0000-implement-rename-task](99c172-0000-implement-rename-task/)
- [ ] [99c172-0001-implement-convert-task](99c172-0001-implement-convert-task/)
- [ ] [99c172-0002-implement-promote-task](99c172-0002-implement-promote-task/)
<!-- subtask-list-end -->

## Notes

Supersedes `77fe7b-add-promote-task-to-subtask-script` (backlog) — that task
covered only `promote-to-subtask.sh`; this task covers all three operations.
`77fe7b` has been marked wont-do.
