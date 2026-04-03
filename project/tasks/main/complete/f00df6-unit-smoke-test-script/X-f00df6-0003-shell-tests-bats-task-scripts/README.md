# Task: shell-tests-bats-task-scripts

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

Write bats tests for the highest-risk task management shell scripts.

## Context

None of the 27+ shell scripts have automated tests. The highest-risk scripts
are those that perform irreversible state transitions (rename dirs, patch
READMEs, update JSON). Tests use temp directories to avoid touching live tasks.

Priority targets:
- `task-json-helpers.sh` — json_get, json_set_str, json_set_bool; used by almost everything
- `new-user-task.sh` — task creation, README template, index update
- `move-task.sh` — cross-folder moves, source/dest README sync
- `complete-task.sh` — marks task complete, renames dir, patches parent README

Tests live in `tests/unit/shell/`. Each script gets its own `.bats` file.
Use `setup()` / `teardown()` to create/destroy a tmp task tree.

Target: ~5–8 bats test cases per script (~20–25 total).

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
