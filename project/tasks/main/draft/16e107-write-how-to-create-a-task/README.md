# Task: write-how-to-create-a-task

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | draft             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | docs                   |
| Created     | 2026-04-03            |
| Completed   | —                      |
| Next-subtask-id | 0002 |

## Goal

Write `project/tasks/how-to-create-a-task.md` — a practical guide for humans
and AI operators on creating and managing tasks in this repository. The guide
should cover:

1. **When to create a task** — any work outside `/sandbox` requires a task;
   start by checking if one already exists
2. **Task types** — USER-TASK vs USER-SUBTASK vs PIPELINE-SUBTASK; which
   script to use for each (`new-user-task.sh`, `new-user-subtask.sh`,
   `new-pipeline-build.sh`)
3. **Subtask ordering** — NNNN numbers define implementation order; work
   subtasks in ascending order; use `reorder-subtasks.sh` if the order changes
4. **The documentation subtask rule** — every task must include a final subtask
   to create or update documentation before the task can be closed
5. **Closing tasks** — ask before closing; use `complete-task.sh`; X- prefix
   convention; never manually move directories
6. **Lifecycle walk-through** — a concrete example from task creation to
   completion with the exact commands

## Context

There is no operational how-to for creating tasks. `CLAUDE.md` contains rules
and script references, but not a step-by-step guide. `project/tasks/README.md`
documents the system structure. `2da360-document-flexible-task-system-usage`
(in draft) covers the task system as a general-purpose abstraction — it is
conceptual, not operational.

The documentation subtask rule (`all new tasks must have a final doc subtask`)
emerged during the pipeline-record-replay epic and needs to be captured
somewhere a human operator will find it.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [ ] [16e107-0000-write-how-to-create-a-task-guide](16e107-0000-write-how-to-create-a-task-guide/)
- [ ] [16e107-0001-update-task-readme-with-doc-rule](16e107-0001-update-task-readme-with-doc-rule/)
<!-- subtask-list-end -->

## Notes

_None._
