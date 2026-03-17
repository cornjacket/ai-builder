# Task: update-target-scripts

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | c98d7b-incremental-subtask-ids             |
| Priority    | —           |

## Goal

Mirror all script changes from the previous subtasks into the `target/`
copies:

- `target/project/tasks/scripts/new-user-subtask.sh`
- `target/project/tasks/scripts/new-pipeline-subtask.sh`
- `target/project/tasks/scripts/complete-task.sh`
- `target/project/tasks/scripts/list-tasks.sh`
- Any other scripts in `target/` that were updated

The `target/` scripts are installed into pipeline-managed repos by
`setup-project.sh`. They must stay in sync with the `project/tasks/scripts/`
versions or the pipeline will behave differently from the development environment.

## Context

`target/` is a snapshot of the task system that gets bootstrapped into each
new sandbox. Changes to the canonical scripts in `project/tasks/scripts/`
must be propagated here manually as part of every scripts task.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
