# Task: claude-pipeline-regression

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | ec6a38-bug-gemini-tester-cannot-read-job-doc             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Run a user-service regression with Claude to confirm the inlined Test Command
change does not break existing Claude behaviour — TESTER still receives the
command correctly and the pipeline completes end-to-end.

## Context

Run with `default.json`. Verify:
- Pipeline completes with `HANDLER_ALL_DONE`
- All TESTER invocations emit `TESTER_TESTS_PASS`
- Gold test passes
- Token counts are not materially higher than the current baseline
  (inlining adds a small amount of text to the TESTER prompt)

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
