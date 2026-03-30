# Task: bug-pipeline-subtask-not-marked-complete

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Next-subtask-id | 0001 |

## Goal

The last pipeline subtask (e.g. `integrate`) is not marked `[x]` in the
build-N README when the pipeline completes. Root cause: `complete-task.sh`
user-subtask path ignores `--skip-rename`, prematurely renaming the build
directory before the orchestrator can write the final metrics and README.

## Context

When `advance-pipeline.sh` walks up after the last subtask and the grandparent
is a human-owned user task, it calls `complete-task.sh --skip-rename` to defer
the build-N directory rename. But the user-subtask code path ignores
`--skip-rename` and renames immediately. This invalidates `top_task_json`,
so the final `render_task_readme` call silently fails, leaving `[ ]` for the
last subtask in the README.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-367963-0000-fix-subtask-completion-and-gold-test](X-367963-0000-fix-subtask-completion-and-gold-test/)
<!-- subtask-list-end -->

## Notes

_None._
