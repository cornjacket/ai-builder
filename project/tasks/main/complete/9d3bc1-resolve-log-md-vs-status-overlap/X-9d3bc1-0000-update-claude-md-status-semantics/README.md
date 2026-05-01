# Task: update-claude-md-status-semantics

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 9d3bc1-resolve-log-md-vs-status-overlap             |
| Priority    | —           |
| Created     | 2026-05-01            |
| Completed | 2026-05-01 |
| Next-subtask-id | 0000               |

## Goal

Replace the `## Session Status` rule in `CLAUDE.md` to reflect the new
status model defined in the parent task's Resolution.

## Context

See parent task Resolution for the full design. Key edits required:

- **Drop the "sign off" semantic entirely** — remove the paragraph that
  defines sign-off as the trigger to write `project/status/YYYY-MM-DD.md`.
- **Introduce "write a status report"** as the new canonical trigger
  phrase, with recognized variants: "status report", "draft a status
  report", "write status", "write up the period".
- **Reframe status as a delta document** — "what happened since the last
  status," not a daily snapshot. State that cadence is operator-driven
  (weekly, twice-weekly, daily) and not tied to session boundaries.
- **Document the roles split:**
  - `log.md` — atomic, per-task, hash-indexed history (unchanged).
  - `project/status/YYYY-MM-DD.md` — periodic synthesis covering the
    period since the prior status. Sections: Work Completed (summary,
    not 1:1 restatement of log.md), Work In Progress, Next Up, Key
    Decisions.
- **Keep "read most recent at session start"** — that part of the
  existing rule still applies.
- **Naming:** keep `YYYY-MM-DD.md` as the as-of date.
- **Cross-worktree:** status remains main-only.

Touchpoint: `CLAUDE.md` — `## Session Status` section (and any other
`sign off` references in the file).

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
