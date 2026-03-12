# Task Management

This directory contains all tasks for the project, organized by epic and
status. Tasks are managed using the scripts in `scripts/` and consumed by
both human developers and AI coding agents.

---

## Structure

```
project/tasks/
    <epic>/                     # one directory per epic (e.g. main)
        README.md               # epic description and status summary
        inbox/                  # raw ideas, not yet evaluated
        draft/                  # being written up, incomplete
        backlog/                # refined, ordered by priority, ready to pull
        in-progress/            # actively being worked on
        complete/               # done and verified
        wont-do/                # explicitly decided against, kept for reference
    scripts/
        new-task.sh             # create a task or subtask (--parent for subtasks)
        move-task.sh            # move a task to a different status
        complete-task.sh        # mark a task or subtask done/undone
        delete-task.sh          # soft-delete a task
        restore-task.sh         # reverse a soft-delete
        show-task.sh            # print a task README to stdout
        list-tasks.sh           # display the task tree
        task-template.md        # README template for top-level tasks
        subtask-template.md     # README template for subtasks
```

---

## Workflow Rules

**Before beginning any task or subtask:** describe its purpose and list all
subtasks in order. If the task manager is human, wait for their approval
before starting any implementation work.

**When picking up work:** pull from `backlog/` in top-to-bottom order.
**When starting a task:** move it to `in-progress/` using `move-task.sh`.
**When done:** run `complete-task.sh` — no `--parent` for top-level tasks,
add `--parent` for subtasks.

---

## Task Format

Each task is a **directory** containing a `README.md`. The directory name is
the task name in kebab-case, prefixed with a short unique ID (e.g.
`a3f2c1-my-task`).

**Task README header:**

```markdown
# Task: <name>

| Field    | Value  |
|----------|--------|
| Status   | draft  |
| Epic     | main   |
| Tags     | —      |
| Parent   | —      |
| Priority | HIGH   |
```

Valid Priority values: `CRITICAL`, `HIGH`, `MED`, `LOW`, `—` (unset).

**Subtask Status is binary.** Subtasks have only two valid Status values:

| Value | Meaning |
|---|---|
| `—` | Not yet done |
| `complete` | Done |

Use `complete-task.sh --parent` to mark a subtask done.

---

## Status Directories

| Status | Meaning |
|---|---|
| `inbox` | Raw idea, captured as-is. Not yet evaluated. |
| `draft` | Being written up. Description is incomplete. |
| `backlog` | Refined and ready to pull. Ordered by priority. |
| `in-progress` | Actively being worked on. |
| `complete` | Done and verified. |
| `wont-do` | Explicitly decided against. Kept for reference. |

---

## Scripts

All scripts should be run from the **repo root**.

```bash
# Create a new top-level task
project/tasks/scripts/new-task.sh --epic main --folder draft --name my-task

# Create a subtask
project/tasks/scripts/new-task.sh --epic main --folder draft \
    --parent my-task --name my-subtask

# Move a task to a different status
project/tasks/scripts/move-task.sh --epic main --name my-task \
    --from draft --to backlog

# Mark a top-level task complete
project/tasks/scripts/complete-task.sh --epic main --folder in-progress --name my-task

# Mark a subtask complete
project/tasks/scripts/complete-task.sh --epic main --folder in-progress \
    --parent my-task --name my-subtask

# List outstanding tasks
project/tasks/scripts/list-tasks.sh --epic main --folder in-progress --depth 2

# List all tasks including completed
project/tasks/scripts/list-tasks.sh --epic main --all
```
