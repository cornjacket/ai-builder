# Task: add-retry-count-to-run-summary

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | orchestrator-core      |
| Created     | 2026-04-05            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Add a total retry count to the run summary — both in `task.json`
(`run_summary.retry_count`) and in the rendered Run Summary table in the
pipeline task README. A retry is any IMPLEMENTOR or TESTER invocation that
was not the first attempt on its component.

## Context

The `warnings` list in `run_summary` already records each retry as a string
(e.g. `RETRY: IMPLEMENTOR on integrate-platform (reason: TESTER_TESTS_FAIL)`).
The count is derivable from `len(warnings)` but is not surfaced anywhere
visible. Having it as a top-level field makes it immediately scannable in
run-history and usable as a health signal when comparing runs over time.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
