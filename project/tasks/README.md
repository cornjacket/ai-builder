# Task Management

This directory contains all tasks for the ai-builder project, organized by
epic and status. Tasks are managed using the scripts in `scripts/` and consumed
by both human developers and AI coding agents.

---

## Structure

```
project/tasks/
    <epic>/                     # one directory per epic (e.g. main, dashboard)
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
        complete-task.sh        # mark a task or subtask done/undone (--parent for subtasks)
        delete-task.sh          # soft-delete: hides directory, removes from parent README
        restore-task.sh         # reverse a soft-delete: unhides directory, re-adds to parent README
        show-task.sh            # print a task's README to stdout
        list-tasks.sh           # display the task tree (--depth, --root, --folder, --all)
        wont-do-subtask.sh      # mark a subtask wont-do: sets Status, removes from parent list
        task-template.md        # README template for top-level tasks
```

---

## Task Format

Each task is a **directory** containing a `README.md` that describes the task.
The directory name is the task name in kebab-case. Tasks are not numbered —
order within a status is determined by position in the status `README.md`.

**Task directory structure:**

```
some-task/
    README.md           # task description, metadata, subtask list
    subtask-one/        # subtask (same structure as a task)
        README.md
    subtask-two/
        README.md
```

**Task README.md header:**

Every task README begins with a metadata table:

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

**Subtask Status is binary.** Subtasks don't move between status folders — their
`Status` field has only two valid values:

| Value | Meaning |
|---|---|
| `—` | Not yet done |
| `complete` | Done |

Use `complete-task.sh --parent` to mark a subtask done; this updates both the
`Status` field and the `[x]` checkbox in the parent README.

Followed by `## Description`, `## Documentation`, `## Subtasks`, and `## Notes` sections
for top-level tasks. Subtask READMEs have `## Description` and `## Notes` only.

The `## Documentation` section is where the author records what public documentation
(if any) this task requires and where it belongs (e.g. this README, `CLAUDE.md`,
inline code comments). Write "none needed" if the task requires no external documentation.

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

## Status Directories

Each status directory contains a `README.md` that lists its tasks in priority
order (top = highest priority). This ordered list is the single source of truth
for task ordering — to reprioritise, edit the list directly.

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

All scripts are in `project/tasks/scripts/` and should be run from the
**repo root**.

```bash
# Create a new top-level task
project/tasks/scripts/new-task.sh --epic main --folder draft --name my-task

# Create a task with priority
project/tasks/scripts/new-task.sh --epic main --folder draft --name my-task --priority HIGH

# Create a subtask under an existing task
project/tasks/scripts/new-task.sh --epic main --folder draft \
    --parent my-task --name my-subtask

# Move a task (and all its subtasks) to a different status
project/tasks/scripts/move-task.sh --epic main --name my-task \
    --from draft --to backlog

# Mark a top-level task complete (moves to complete/)
project/tasks/scripts/complete-task.sh --epic main --folder in-progress --name my-task

# Mark a subtask complete (updates checkbox and Status field)
project/tasks/scripts/complete-task.sh --epic main --folder in-progress \
    --parent my-task --name my-subtask

# Undo either
project/tasks/scripts/complete-task.sh --epic main --folder in-progress --name my-task --undo
project/tasks/scripts/complete-task.sh --epic main --folder in-progress \
    --parent my-task --name my-subtask --undo

# Print a task's README to stdout
project/tasks/scripts/show-task.sh --epic main --folder in-progress --name my-task
project/tasks/scripts/show-task.sh --epic main --folder in-progress \
    --parent my-task --name my-subtask

# Soft-delete a task (hides directory, removes from parent README)
project/tasks/scripts/delete-task.sh --epic main --folder draft --name my-task
project/tasks/scripts/delete-task.sh --epic main --folder draft \
    --parent my-task --name my-subtask

# Restore a soft-deleted task (unhides directory, re-appends to parent README)
project/tasks/scripts/restore-task.sh --epic main --folder draft --name my-task
project/tasks/scripts/restore-task.sh --epic main --folder draft \
    --parent my-task --name my-subtask

# Mark a subtask as wont-do (sets Status, removes from parent list, keeps directory)
project/tasks/scripts/wont-do-subtask.sh --epic main --folder in-progress \
    --parent my-task --name my-subtask

# List incomplete tasks in an epic (default)
project/tasks/scripts/list-tasks.sh --epic main

# List all tasks including completed subtasks
project/tasks/scripts/list-tasks.sh --epic main --all

# List incomplete tasks in a specific status, with subtask depth
project/tasks/scripts/list-tasks.sh --epic main --folder in-progress --depth 2

# Filter by tag across all statuses
project/tasks/scripts/list-tasks.sh --epic main --tag backend --depth 2 --all

# List tasks rooted at a specific directory
project/tasks/scripts/list-tasks.sh --root main/in-progress/my-task --depth 3

# Write the absolute path of a task README to current-job.txt (for pipeline use)
project/tasks/scripts/set-current-job.sh \
    --output-dir <pipeline-output-dir> \
    <path-to-task-README.md>

# Check whether a task is the last (integration) subtask (exit 0 = yes, 1 = no)
project/tasks/scripts/is-last-task.sh <path-to-task-README.md>
```

---

## Epics

| Epic | Description |
|---|---|
| `main` | Default epic. Core ai-builder platform work. |
