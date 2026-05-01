# Task: update-project-status-readme

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

Update `project/status/README.md` to match the new status model defined
in the parent task's Resolution.

## Context

The current README likely describes status as a daily sign-off doc. After
this subtask it must describe status as:

- A **delta document** covering the period since the previous status
  (not a daily snapshot).
- Triggered by the operator phrase **"write a status report"** (no
  longer tied to "sign off" or session end).
- Cadence is flexible (weekly, twice-weekly, daily) — operator's choice.
- Sections: Work Completed (summary of the period, not a 1:1 restatement
  of `log.md`), Work In Progress, Next Up, Key Decisions.
- Naming: `YYYY-MM-DD.md` as the as-of date.
- Status is main-only (not produced from feature worktrees).
- Relationship to `log.md`: log.md is atomic per-task ground truth;
  status is the human narrative synthesis layered on top.

Touchpoints:
- `project/status/README.md` — primary doc for the status model.
- `project/README.md` — has a `## Sign-off` section and inline references
  to "sign off" / "sign-off" that must be reframed in the same terms
  (delta doc, "write a status report" trigger, flexible cadence).

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
