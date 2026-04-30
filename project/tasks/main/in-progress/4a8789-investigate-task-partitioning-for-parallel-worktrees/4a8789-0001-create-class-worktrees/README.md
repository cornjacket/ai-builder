# Task: create-class-worktrees

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 4a8789-investigate-task-partitioning-for-parallel-worktrees             |
| Priority    | —           |
| Created     | 2026-04-03            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Create git worktrees for the partition classes that are ready to be worked in
parallel, using the branch names defined in the class definitions document.

## Context

**Class definitions:** [`project/tasks/classes.md`](../../../../../../project/tasks/classes.md)

Classes ready to start in parallel right now (no orchestrator.py conflicts):

- **Class 3 — Acceptance Spec** → branch `acceptance-spec`
- **Class 5 — Regression Infrastructure** → branch `regression-infra`
- **Class 6 — Task Management & Dev Tooling** → branch `task-tooling`
- **Class 7 — Documentation** → branch `docs`

Classes to defer until Class 1 (Gemini compat, already in-progress) is merged:

- **Class 2 — Orchestrator Core** → branch `orchestrator-core`

Classes that can start any time but are lower priority:

- **Class 4 — New Pipeline Modes** → branch `new-pipelines`
- **Class 8 — Workspace & Infrastructure** → branch `workspace-mgmt`

**To create a worktree:**
```bash
bash bootstrap/new-worktree.sh <branch-name>
```

Create only the worktrees that will be actively worked. Do not create all 8 at once.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
