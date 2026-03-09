# AI Agent Instructions — ai-builder

## Task Management

All work in this repository is tracked through a structured task management
system. Before starting any work, check the task system to understand current
priorities and status.

**Full documentation:** [`project/tasks/README.md`](project/tasks/README.md)

### Summary

Tasks are organized by epic and status. Each task is a directory containing a
`README.md` that describes the work. Subtasks are subdirectories of their
parent task.

```
project/tasks/
    <epic>/
        inbox/        # raw ideas, not yet evaluated
        draft/        # being written up
        backlog/      # refined, ordered by priority — pull from here
        in-progress/  # actively being worked on
        complete/     # done and verified
        wont-do/      # explicitly decided against
```

**When picking up work:** pull from `backlog/` in top-to-bottom order.
**When starting a task:** move it to `in-progress/` using `move-task.sh`.
**When done:** move it to `complete/` using `move-task.sh`.

### Scripts

Run from the repo root:

```bash
project/tasks/scripts/new-task.sh    --epic main --folder draft --name <task-name>
project/tasks/scripts/new-subtask.sh --epic main --folder draft --parent <task> --name <subtask>
project/tasks/scripts/move-task.sh   --epic main --name <task> --from <status> --to <status>
project/tasks/scripts/list-tasks.sh  --epic main
```

