# Task: resolve-log-md-vs-status-overlap

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | in-progress             |
| Epic        | main               |
| Tags        | —               |
| Priority    | HIGH           |
| Category    | task-tooling           |
| Created     | 2026-04-30            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Resolve the overlap between `log.md` (per-task, hash-indexed, repo root)
and `project/status/YYYY-MM-DD.md` (per-session, sign-off doc) so the two
artifacts have non-redundant, well-defined roles. Update CLAUDE.md to
reflect the resolution.

## Context

We currently maintain two parallel write streams describing what has
shipped:

- **`log.md`** — append-only, one entry per task, ends in a short commit
  hash. Enforced by CLAUDE.md's `## Work Log` rule and lesson 038. Lives
  at the repo root and is a documented portable pattern (also used in
  `ai-engineering-sandbox/document-analyzer`).

- **`project/status/YYYY-MM-DD.md`** — per-session sign-off doc with
  Work Completed / Work In Progress / Next Up / Key Decisions sections.
  Loaded automatically at session start per CLAUDE.md's "Session Status"
  rule. Local convention only.

The overlap is real: status docs' "Work Completed" sections restate the
same task closures that already live as log.md entries. Today (2026-04-30)
the operator surfaced this directly: are we duplicating? The honest
answer is partially. The unique value of each is:

- **log.md uniquely**: hash index, atomic per-task delta, scannable
  across long history with `grep`.
- **status uniquely**: In-Progress, Next-Up, Key Decisions — i.e.,
  *intent* and *forward-looking state*, not just history.

**Open questions to resolve in this task:**

1. Should status's "Work Completed" be deprecated in favour of a link to
   the day's log.md entries (`grep '^- \*\*2026-04-30\*\*' log.md`)?
2. Should status be reframed entirely around its unique value
   (in-progress + next-up + decisions), with history left to log.md?
3. Should sign-off be auto-generatable from log.md plus the current
   in-progress folder state, removing the manual restate step?
4. What is the canonical answer when an operator says "where are we" —
   log.md tail, status tail, or `list-tasks.sh --folder in-progress`?
5. Cross-worktree: status is per-session-on-main; log.md is per-commit.
   Do parallel worktrees need their own status docs, or is log.md
   sufficient because it's hash-indexed?

**Approach:** write a short design note in `sandbox/log-vs-status.md`
analysing the overlap, propose a resolution, get operator approval,
then update CLAUDE.md (`## Work Log` and `## Session Status` sections)
and possibly add or refactor a sign-off helper script.

## Subtasks

(To be added after the design note is approved. Likely:
write the design note, update CLAUDE.md, add/refactor sign-off helper,
final docs subtask.)

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
