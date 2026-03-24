# Task: no-history-flag-in-state-machine

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | b14e76-brainstorm-token-usage-and-caching-costs/b14e76-0000-strip-tester-handoff-history             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Add a `no_history` boolean field to each role entry in the state machine JSON. The orchestrator reads this at load time to build the set of roles that receive no handoff history, replacing the hardcoded `_HANDLER_ROLES` set in Python.

## Context

`_HANDLER_ROLES` is currently a hardcoded Python set. Changing which roles get history requires editing source code. Moving this to the JSON makes it a configuration decision: different machine files can have different history policies, and experimentation requires only a JSON edit.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
