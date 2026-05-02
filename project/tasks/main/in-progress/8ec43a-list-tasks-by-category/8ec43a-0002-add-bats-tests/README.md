# Task: add-bats-tests

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 8ec43a-list-tasks-by-category             |
| Priority    | —           |
| Created     | 2026-05-02            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Add bats coverage for the two new flags. Reuse the existing test fixture
pattern (e.g. `project/tasks/scripts/tests/`). Cases:

1. `--category <branch>` filters to matching tasks only.
2. `--category unclassified` matches `Category: —` and missing-field tasks.
3. `--category <unknown>` produces an empty list (no error).
4. `--group-by-category` groups tasks under `[<category>]` sub-headings in
   the canonical class order with `unclassified` last.
5. `--group-by-category --sort-priority` orders HIGH→MED→LOW→unset within
   each group.
6. `--category` + `--group-by-category` combined yields a single group.

## Context

Find existing bats tests for `list-tasks.sh` (or its sibling scripts) and
extend in place rather than creating a new test file unless none exist.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
