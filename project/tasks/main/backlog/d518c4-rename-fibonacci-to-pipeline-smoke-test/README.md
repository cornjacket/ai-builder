# Task: rename-fibonacci-to-pipeline-smoke-test

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | regression-infra       |
| Created     | 2026-04-04            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Rename `tests/regression/fibonacci/` to `tests/regression/pipeline-smoke-test/`
and update all references. The fibonacci name describes the test subject, not
the pipeline capability being exercised — pipeline-smoke-test is clearer.

## Context

The fibonacci test verifies the most basic pipeline capability: a flat atomic
build (no decomposition, single ARCHITECT → IMPLEMENTOR → TESTER cycle). It
is a smoke test for the pipeline, not a fibonacci-specific test. Renaming
makes its role in the regression suite self-evident.

**Changes required:** `git mv`, update `tests/regression/README.md` index,
update any references in task READMEs or documentation.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
