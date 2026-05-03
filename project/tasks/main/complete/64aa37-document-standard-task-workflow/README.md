# Task: document-standard-task-workflow

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Priority    | HIGH           |
| Category    | docs           |
| Created     | 2026-05-03            |
| Completed | 2026-05-03 |
| Next-subtask-id | 0001 |

## Goal

Add a `### Standard task workflow` recipe to the
`## Development Workflow (Git Worktrees)` section of `CLAUDE.md` — a
single end-to-end numbered list (1..N) tying together task triage,
worktree setup, per-subtask commits, log entries, task close, and
worktree teardown.

The recipe must be the first thing an operator (human or AI) reads,
and must reference (not duplicate) the deeper sections — Task
Management, Git Commits, Work Log — for full detail.

## Context

The pieces of the workflow are already documented across CLAUDE.md, but
no single section walks through the full loop. This was the missing
prerequisite for parallel implementation: with `--group-by-category`
just landed (`8ec43a-list-tasks-by-category`), an operator can now pick
the next backlog item per worktree class — but the recipe for what to
do with that pick lives in three different sections. This task pins the
end-to-end loop in one place.

The recipe should not introduce new behaviour; only existing scripts
are referenced.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-64aa37-0000-add-recipe-to-claude-md](X-64aa37-0000-add-recipe-to-claude-md/)
<!-- subtask-list-end -->

## Notes

_None._
