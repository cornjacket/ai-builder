# Task: remove-new-task-sh

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | wont-do |
| Epic        | main               |
| Tags        | —               |
| Parent      | f7a6af-redefine-task-system-human-pipeline-boundary             |
| Priority    | —           |

## Goal

Delete `new-task.sh` from both `project/tasks/scripts/` and
`target/project/tasks/scripts/` once the TM agent prompt has been updated
to use `new-pipeline-subtask.sh` instead.

## Context

`new-task.sh` is currently deprecated (marked with a comment) but still
present because the TM agent prompt calls it to create pipeline component
subtasks. It cannot be deleted until 191773 (update-aibuilder-claude-md)
or the TM prompt update is complete and `new-pipeline-subtask.sh` is in use.

Steps:
1. Verify the TM prompt no longer references `new-task.sh`
2. Delete `project/tasks/scripts/new-task.sh`
3. Delete `target/project/tasks/scripts/new-task.sh`
4. Remove the `check_file` and `check_exec` entries for `new-task.sh` from `verify-setup.sh`
5. Remove any remaining references in README docs (c8422d handles most of these)

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
