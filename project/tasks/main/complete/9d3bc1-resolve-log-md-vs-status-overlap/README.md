# Task: resolve-log-md-vs-status-overlap

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Priority    | HIGH           |
| Category    | task-tooling           |
| Created     | 2026-04-30            |
| Completed | 2026-05-01 |
| Next-subtask-id | 0003 |

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

## Resolution

Reframe status as a **delta document** — "what happened since the last
status" — rather than a daily snapshot. Cadence becomes flexible (weekly,
twice-weekly, daily) at operator's choice, mirroring a real staff status
meeting.

**Roles after the change:**
- `log.md` — atomic, per-task, hash-indexed ground truth (unchanged).
- `project/status/YYYY-MM-DD.md` — periodic synthesis covering the period
  since the previous status. Sections: Work Completed (summary of the
  period, not a 1:1 restatement of log.md), Work In Progress, Next Up,
  Key Decisions.

**Trigger phrase:** the old "sign off" semantic is dropped entirely.
Replaced by **"write a status report"** as the canonical operator phrase
to produce a new status doc. CLAUDE.md must recognize this phrase (and
natural variants: "status report", "draft a status report", "write
status", "write up the period") as the trigger.

**Naming:** keep `YYYY-MM-DD.md` as the as-of date of the status.

**Cross-worktree:** status remains main-only (coordination artifact, not
per-worktree state).

**Open questions resolved:**
1. "Work Completed" stays, but as a summary spanning the period, not a
   daily restatement of log.md entries.
2. Status keeps both backward (synthesis) and forward (in-progress,
   next-up, decisions) sections.
3. Helper to draft "Work Completed" from `log.md` between dates:
   optional, defer.
4. Canonical "where are we": latest status for narrative;
   `list-tasks.sh --folder in-progress` for live state.
5. Status stays main-only; log.md (hash-indexed) is sufficient
   cross-worktree history.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-9d3bc1-0000-update-claude-md-status-semantics](X-9d3bc1-0000-update-claude-md-status-semantics/)
- [x] [X-9d3bc1-0001-update-project-status-readme](X-9d3bc1-0001-update-project-status-readme/)
- [x] [X-9d3bc1-0002-update-repo-readme-with-status-pointer](X-9d3bc1-0002-update-repo-readme-with-status-pointer/)
<!-- subtask-list-end -->

## Notes

_None._
