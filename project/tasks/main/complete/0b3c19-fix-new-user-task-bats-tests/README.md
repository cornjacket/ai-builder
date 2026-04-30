# Task: fix-new-user-task-bats-tests

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Priority    | HIGH           |
| Category    | task-tooling           |
| Created     | 2026-04-30            |
| Completed | 2026-04-30 |
| Next-subtask-id | 0000               |

## Goal

Restore green main: update `tests/unit/shell/test_new_user_task.bats` to pass
`--category` (now required) on every invocation, and add a regression test
asserting the script fails when `--category` is missing.

## Context

Commit `9381b23` (Close 4a8789-0000-add-category-flag-to-new-user-task) made
`--category` required in `new-user-task.sh`. The bats suite was not updated
in the same commit, so 5 tests now fail on push to main (CI run 25186231082):
`#16, #17, #18, #19, #20`. Each calls `new-user-task.sh` without
`--category`. The fix is mechanical: add `--category task-tooling` (or any
valid class) to each invocation. Add one new test that asserts the script
exits non-zero when `--category` is omitted, mirroring the existing
`fails when --folder is missing` test.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
