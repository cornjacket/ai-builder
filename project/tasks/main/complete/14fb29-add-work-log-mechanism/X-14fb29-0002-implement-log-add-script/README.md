# Task: implement-log-add-script

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 14fb29-add-work-log-mechanism             |
| Priority    | —           |
| Created     | 2026-04-30            |
| Completed | 2026-04-30 |
| Next-subtask-id | 0000               |

## Goal

Implement `scripts/log-add.sh` with two modes:

- `scripts/log-add.sh --task <name> [--subtask <name>] -- <description>` —
  appends a new entry to `log.md` with today's date and `_pending_` as the
  hash placeholder.
- `scripts/log-add.sh --backfill` — replaces the most recent `_pending_`
  in `log.md` with `git rev-parse --short HEAD` (no commit).

## Context

Validates that `<task>` resolves to an existing task directory under
`project/tasks/<epic>/{draft,backlog,in-progress,complete}/`. Enforces format
consistency so entries don't drift. The `--backfill` mode leaves `log.md`
dirty; the change rides into the next task's commit per lesson 038.

No combined "update + commit" mode — commits in this repo use task trailers
and varying message bodies, and a wrapper would be too rigid.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
