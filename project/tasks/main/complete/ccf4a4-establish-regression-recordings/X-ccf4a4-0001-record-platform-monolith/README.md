# Task: record-platform-monolith

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | ccf4a4-establish-regression-recordings             |
| Priority    | —           |
| Created     | 2026-04-04            |
| Completed | 2026-04-05 |
| Next-subtask-id | 0000               |

## Goal

Establish the first recording for the `platform-monolith` regression and add replay
infrastructure so future runs can execute without AI invocations.

## Context

Has 2 prior live runs but no recording or replay scripts yet.

**Steps:** see parent task `ccf4a4-establish-regression-recordings` for the
full per-subtask procedure.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

Blocked until `f5f7b8-pipeline-acceptance-spec-writer` (worktree: `acceptance-spec`)
is merged to main. Re-record after that merge so the recording captures the
updated pipeline behaviour (integrate-\<scope\> naming, ACCEPTANCE_SPEC_WRITER stage).
Previous recording attempt (2026-04-04) was discarded — failed TestRetryWarnings
(2 IMPLEMENTOR retries on integrate-platform and integrate-store).
