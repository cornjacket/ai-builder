# Task: compare-token-usage-with-historical-runs

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 403a88-role-doc-size-audit             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

After trimming role docs, run a platform-monolith regression and compare
token usage and elapsed time against the current best eligible baseline
(run 14: 26m 6s, 75,061 tokens out, 2,538,065 cached). Record results
in the regression run-history and confirm gold test passes.

## Context

This is the validation step for the role-doc-size-audit task. The
comparison should cover:
- Per-role cached token totals vs baseline
- Total elapsed time vs baseline
- Gold test pass/fail

If savings are negligible (< 1% cached reduction), note that in the
run history and close the task as complete — the effort ceiling is low.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
