# Task: add-spec-coverage-checker

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | f5f7b8-pipeline-acceptance-spec-writer             |
| Priority    | —           |
| Created     | 2026-04-04            |
| Completed | 2026-04-04 |
| Next-subtask-id | 0000               |

## Goal

Create the deterministic spec coverage checker: a script that runs after
IMPLEMENTOR at the TOP integrate level, before TESTER, and verifies that the
generated test files cover every endpoint in `acceptance-spec.json`.

## Context

No AI involved — this is a pure string/regex check. For each endpoint entry
in `acceptance-spec.json`, scan the generated test files to confirm at least
one test references the method+path pair. If any endpoint is uncovered, fail
fast with a coverage report listing the missing endpoints.

The checker runs only at TOP integrate level. It is a no-op if
`acceptance-spec.json` has an empty endpoints array.

Deliverables:
- `ai-builder/orchestrator/agents/builder/spec-coverage-checker.py` (or `.sh`)
- `ai-builder/orchestrator/agents/builder/spec-coverage-checker.md` — companion doc
- State machine wiring: new state after IMPLEMENTOR, before TESTER, at TOP integrate

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
