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
        new-task.sh             # create a new task
        new-subtask.sh          # create a subtask under an existing task
        move-task.sh            # move a task to a different status
        list-tasks.sh           # display the full task tree for an epic
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

| Field  | Value  |
|--------|--------|
| Status | draft  |
| Epic   | main   |
| Tags   | —      |
| Parent | —      |
```

Followed by `## Description`, `## Subtasks`, and `## Notes` sections.

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
# Create a new task
project/tasks/scripts/new-task.sh --epic main --folder draft --name my-task

# Create a subtask under an existing task
project/tasks/scripts/new-subtask.sh --epic main --folder draft \
    --parent my-task --name my-subtask

# Move a task (and all its subtasks) to a different status
project/tasks/scripts/move-task.sh --epic main --name my-task \
    --from draft --to backlog

# List all tasks in an epic
project/tasks/scripts/list-tasks.sh --epic main

# List tasks in a specific status
project/tasks/scripts/list-tasks.sh --epic main --folder backlog
```

---

## Epics

| Epic | Description |
|---|---|
| `main` | Default epic. Core ai-builder platform work. |
