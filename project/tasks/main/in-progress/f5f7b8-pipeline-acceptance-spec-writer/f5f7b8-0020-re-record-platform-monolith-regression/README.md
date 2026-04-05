# Task: re-record-platform-monolith-regression

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | f5f7b8-pipeline-acceptance-spec-writer             |
| Priority    | —           |
| Created     | 2026-04-05            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Re-run the platform-monolith regression using `record.sh --force` so that the
recording is pushed to ai-builder-recordings. Run 5 (2026-04-04) was run via
`run.sh` and was never recorded or pushed.

## Context

Platform-monolith has a `run.sh` that runs the pipeline without `--record-to`.
That script was used for run 5, which left no recording in ai-builder-recordings.
`run.sh` has since been deleted; `record.sh` is now the only way to run a
regression. This subtask re-records with the fixed pipeline (ACCEPTANCE_SPEC_WRITER
injecting goal/context from task_state) and pushes the recording.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
