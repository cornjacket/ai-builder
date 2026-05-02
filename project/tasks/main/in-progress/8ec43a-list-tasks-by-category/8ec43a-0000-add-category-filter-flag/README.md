# Task: add-category-filter-flag

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

Add `--category <branch>` to `list-tasks.sh`. When set, only tasks whose
`Category:` field matches the given value are listed; `unclassified` is a
valid filter value matching tasks with `Category: —` or no Category field.

Implementation mirrors the existing `--tag` plumbing: a `get_category()`
helper alongside `get_priority()`, and a `matches_category()` predicate
called from `print_status_tasks` and `print_dir_tasks` next to `has_tag`.

## Context

`Category:` is set on USER-TASKs only. Subtasks inherit from their parent
implicitly and don't carry the field. The filter therefore only fires at
the top-level task layer; deeper recursion is unaffected.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
