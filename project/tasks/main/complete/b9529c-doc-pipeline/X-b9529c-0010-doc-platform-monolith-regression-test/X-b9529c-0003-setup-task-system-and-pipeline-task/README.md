# Task: setup-task-system-and-pipeline-task

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | b9529c-doc-pipeline/b9529c-0009-doc-platform-monolith-regression-test             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Verify `reset.sh` correctly sets up the sandbox output directory and task tree.

## Context

Run `tests/regression/doc-platform-monolith/reset.sh` and confirm:
- `sandbox/doc-platform-monolith-output/` exists with the correct file tree
- The two retained `.md` files are present in the output
- No other `.md` files exist in the output before the pipeline runs
- `sandbox/doc-platform-monolith-target/` has the USER-TASK and PIPELINE-SUBTASK
- `current-job.txt` points at the `doc-1` README with `Level: TOP`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
