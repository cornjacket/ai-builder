# Task: python-tests-render-and-index

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | f00df6-unit-smoke-test-script             |
| Priority    | —           |
| Created     | 2026-04-02            |
| Completed | 2026-04-02 |
| Next-subtask-id | 0000               |

## Goal

Write unit tests for `render_readme.py` and `build_master_index.py` —
the two highest-value untested Python modules that do not require deep mocking.

## Context

`render_readme.py` (204 lines): renders a task README from task.json. Two
modes: TOP-level (full summary + execution log) and non-TOP (subtask list only).
Preserves existing content sections. Pure filesystem I/O — testable with
`tmp_task_dir` fixture.

`build_master_index.py` (202 lines): walks output directory, extracts
Purpose/Tags headers from .md files, builds master-index.md. Preserves
user-written blocks between rebuilds. Also pure filesystem I/O.

Target: ~15 test cases each. Cover happy path, missing fields, re-render
idempotency, user block preservation.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
