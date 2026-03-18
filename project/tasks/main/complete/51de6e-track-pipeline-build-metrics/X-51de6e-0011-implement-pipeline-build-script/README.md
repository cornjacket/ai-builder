# Task: implement-pipeline-build-script

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 51de6e-track-pipeline-build-metrics             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Create `new-pipeline-build.sh` — a script that creates a Level:TOP
PIPELINE-SUBTASK as the entry point for a pipeline run — and document
the pipeline build workflow.

1. Create `project/tasks/scripts/new-pipeline-build.sh`:
   - Wraps `new-pipeline-subtask.sh --level TOP`
   - Args: `--epic <epic> --folder <status> --parent <user-task> --name <name>`
   - Sets `Level: TOP` in the created README metadata
   - Output: path to the created build task README (for use with `set-current-job.sh`)

2. Copy to `target/project/tasks/scripts/new-pipeline-build.sh`

3. Update `CLAUDE.md` with a "Submitting a pipeline build run" section:
   - Requirement: pipeline entry point must be a PIPELINE-SUBTASK with Level: TOP
   - Show the two-step process: `new-pipeline-build.sh` then `set-current-job.sh`

4. Update `ai-builder/orchestrator/README.md` with the same instructions

5. Fix `tests/regression/user-service/reset.sh` to use `new-pipeline-build.sh`
   (create a `build-1` PIPELINE-SUBTASK under the user-task, point
   `current-job.txt` at it — matching the platform-monolith pattern)

## Context

The orchestrator now validates (in TM mode) that the initial job document
is a PIPELINE-SUBTASK with Level: TOP. The user-service regression test
currently fails this check because it submits the user-task directly.
The platform-monolith reset.sh already follows the correct pattern but
does it inline without a dedicated script. This subtask formalises the
pattern and makes it the documented, enforced standard.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
