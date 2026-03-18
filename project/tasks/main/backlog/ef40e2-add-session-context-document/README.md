# Task: add-session-context-document

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | process, docs           |
| Priority    | HIGH                    |
| Next-subtask-id | 0000               |
## Goal

Introduce a `context.md` file written at sign-off alongside the daily status
log, giving the AI a focused, machine-readable snapshot of exactly where work
left off so it can resume without reconstructing context from scratch.

## Context

Currently sign-off writes a human-readable `project/status/YYYY-MM-DD.md`
summary. That document is useful for humans but is narrative — the AI must
infer what to do next from prose. A dedicated `context.md` would be structured
and terse, optimised for AI context restoration at the start of the next session.

**Proposed location:** `project/status/context.md` (single file, overwritten
at each sign-off — always reflects the most recent session).

**Proposed content:**

- `## Current work` — the task(s) actively in progress with full id-names and
  a one-line state description (e.g. "mid-subtask", "blocked on X", "ready to run")
- `## Last action` — the single most recent concrete action taken
- `## Next step` — the immediate next action to take on resuming (specific enough
  to act on without re-reading the status log)
- `## Open decisions` — any unresolved questions or forks that the Oracle needs
  to decide before work can continue
- `## Hot files` — files most likely to need reading at session start

**Sign-off integration:** the sign-off instruction in CLAUDE.md should be
updated to include writing `context.md` as a required step alongside the
daily status log.

**Session-start integration:** the CLAUDE.md session-start instruction
("read the most recent status file") should be updated to also read
`project/status/context.md` if it exists.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
