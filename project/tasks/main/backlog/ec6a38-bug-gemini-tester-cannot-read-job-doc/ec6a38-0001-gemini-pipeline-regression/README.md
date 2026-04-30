# Task: gemini-pipeline-regression

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

Run a full user-service TM regression with Gemini and confirm the pipeline
completes with `HANDLER_ALL_DONE`, TESTER passes on all components, and
the gold test passes.

## Context

Run with `default-gemini.json`. Verify:
- No `TESTER_NEED_HELP` outcomes
- All TESTER invocations emit `TESTER_TESTS_PASS`
- Gold test passes

Record results in `tests/regression/user-service/results/gemini-run-history.md`.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
