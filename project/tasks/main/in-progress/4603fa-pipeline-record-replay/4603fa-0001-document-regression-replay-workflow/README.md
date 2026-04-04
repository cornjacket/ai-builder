# Task: document-regression-replay-workflow

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 4603fa-pipeline-record-replay             |
| Priority    | —           |
| Created     | 2026-04-03            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Document the regression replay workflow for both internal pipeline developers
and end users (customers running the pipeline against their own target repos).

## Context

Discovered during `8985d4-0007-verify-platform-monolith`: a retry occurred
(IMPLEMENTOR on `store`, slice aliasing bug) and the source code from the
failed first attempt was unrecoverable — the retry overwrote it.

The record mechanism (git commit before each AI cycle) solves this. Once
implemented, document:

**For internal pipeline development:**
- How to use replay to debug TESTER failures and retry root causes
- How to compare what different IMPLEMENTOR attempts produced for the same task
- How to analyze patterns in AI mistakes across regression runs

**For end users (customers):**
- The record mechanism is available for their target repos too
- Useful when the pipeline produces unexpected output or a component fails
  intermittently — replay lets them step through each agent's contribution
- Documents how to enable, run with replay, and inspect the commit history
- Explains when saving a recording is necessary (failure/retry) vs optional
  (clean run already has a prior recording)

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
