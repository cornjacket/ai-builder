# Task: unit-tests

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | b9529c-doc-pipeline             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Add unit tests covering all new code from subtasks 0000–0005.

## Context

Tests to add to `tests/unit/test_agents.py` (or a new `test_doc_agents.py`):
- LCHAgent route_on: default outcome when field absent, correct outcome when field matches, error when default key missing from config
- DecomposeAgent: verify component_type=integrate is written to integrate subtask's task.json, and absent from component subtasks
- MarkdownLinterAgent: pass case, fail cases for each check (missing Purpose, missing Tags, empty section, placeholder text), correct outcome token per component_type value
- Protocol conformance: MarkdownLinterAgent satisfies InternalAgent Protocol
- Machine JSON validation: all impl paths in machines/doc/default.json resolve and satisfy Protocol

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
