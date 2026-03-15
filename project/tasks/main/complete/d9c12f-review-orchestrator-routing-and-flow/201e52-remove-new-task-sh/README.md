# Task: remove-new-task-sh

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | d9c12f-review-orchestrator-routing-and-flow             |
| Priority    | —           |

## Goal

Delete `new-task.sh` from both `project/tasks/scripts/` and
`target/project/tasks/scripts/` and remove its checks from `verify-setup.sh`.

## Context

`new-task.sh` is deprecated — replaced by `new-user-task.sh`,
`new-user-subtask.sh`, and `new-pipeline-subtask.sh`. It still exists because
the TM agent prompt calls it to create pipeline component subtasks. It can
only be deleted after the TM prompt is updated to call `new-pipeline-subtask.sh`.

Steps:
1. Update the TM prompt to call `new-pipeline-subtask.sh` instead of `new-task.sh --parent`
2. Delete `project/tasks/scripts/new-task.sh`
3. Delete `target/project/tasks/scripts/new-task.sh`
4. Remove `check_file` and `check_exec` entries for `new-task.sh` from `verify-setup.sh`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
