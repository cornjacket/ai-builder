# Task: add-project-flag-to-task-scripts

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | draft             |
| Epic        | main               |
| Tags        | —               |
| Priority    | MED           |
| Category    | task-tooling           |
| Next-subtask-id | 0000               |
## Goal

Add `--project <name>` support to all task scripts so they can operate on
`project/projects/<name>/<epic>/` in addition to `project/tasks/<epic>/`.

## Context

Currently all task scripts (`new-user-task.sh`, `new-user-subtask.sh`,
`new-pipeline-subtask.sh`, `move-task.sh`, `complete-task.sh`, `show-task.sh`,
`delete-task.sh`, `restore-task.sh`, `list-tasks.sh`, `wont-do-subtask.sh`,
`next-subtask.sh`) resolve paths relative to `project/tasks/`.

With `--project my-project`, the same scripts should resolve relative to
`project/projects/my-project/`. This makes `new-build.sh` unnecessary —
you'd instead use:

```bash
new-pipeline-subtask.sh --project my-project --epic main --folder in-progress \
    --parent my-project --name build-1
```

All scripts in both `project/tasks/scripts/` and `target/project/tasks/scripts/`
must be updated. The `--project` flag is always optional; without it, behaviour
is unchanged.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
