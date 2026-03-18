# Task: list-tasks-sort-priority

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | bc5c01-task-script-cleanup             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Add a `--sort-priority` flag to `list-tasks.sh` (and its copy in `target/`)
that outputs tasks ordered HIGH → MED → LOW → unset instead of alphabetically
by directory name.

Tasks with no priority set (`—`) should appear last. The flag should compose
with existing flags (`--folder`, `--depth`, `--tag`, etc.).

Update both copies:
- `project/tasks/scripts/list-tasks.sh`
- `target/project/tasks/scripts/list-tasks.sh`

## Context

Currently `list-tasks.sh` always sorts alphabetically. When reviewing the
backlog it's useful to see high-priority items first without having to
manually scan for `[HIGH]` tags.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
