# Task: add-update-run-history-script

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | ccf4a4-establish-regression-recordings             |
| Priority    | —           |
| Created     | 2026-04-04             |
| Completed | 2026-04-04 |
| Next-subtask-id | 0000               |

## Goal

Create `tests/regression/lib/update-run-history.sh` — a token-free script that
fills in the Gold and Notes columns on the last row of a run-history.md file.
Update `tests/regression/CLAUDE.md` step 5 to call it instead of manual editing.

## Context

`reset.sh` auto-appends a run-history row from task.json (run number, date,
elapsed, token counts) but leaves Gold and Notes blank because those require
human judgment (did the gold tests pass? what task triggered this run?).
Previously the procedure said to append and fill the row manually — error-prone
and token-wasteful when done via AI. This script replaces that manual step.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
