# Task: gemini-regression-verification

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 024459-bug-gemini-agent-cannot-read-job-doc             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Run a full clean user-service regression using the Gemini agent from reset
to HANDLER_ALL_DONE without any manual intervention or resume steps. All
three components (store, handlers, integrate) must complete in a single
uninterrupted orchestrator run.

## Context

All 8 implementation fixes have been applied (subtasks 0000–0007). The
previous runs required multiple resume steps due to bugs encountered during
the fix campaign. This subtask verifies the fixes hold end-to-end:

1. Reset the sandbox: `reset.sh` on user-service-target and user-service-output
2. Run the orchestrator with the Gemini state machine
3. Confirm HANDLER_ALL_DONE with no NEED_HELP or manual intervention

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
