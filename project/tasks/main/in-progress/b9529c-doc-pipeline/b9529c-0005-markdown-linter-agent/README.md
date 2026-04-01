# Task: markdown-linter-agent

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | b9529c-doc-pipeline             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Implement `agents/doc/linter.py` — the MarkdownLinterAgent (POST_DOC_HANDLER).
Checks all `.md` files written in the current step and emits a typed pass/fail
outcome so the machine JSON can retry the correct role.

## Context

The agent reads `component_type` from `task.json` to determine which outcome to emit:
- atomic step: POST_DOC_HANDLER_ATOMIC_PASS or POST_DOC_HANDLER_ATOMIC_FAIL
- integrate step: POST_DOC_HANDLER_INTEGRATE_PASS or POST_DOC_HANDLER_INTEGRATE_FAIL

Checks to perform on each `.md` file written this step:
- Purpose and Tags headers present (see docs/guidelines/doc-format.md)
- No empty sections (section header followed immediately by next header or EOF)
- No placeholder text (`_To be written._`, `TODO`, etc.)

On fail: include a structured error report in the handoff so the retried role
knows what to fix. Satisfies the `InternalAgent` Protocol. Create `agents/doc/`
directory with a `README.md`.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
