# Task: remove-request-functionality

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | PIPELINE-SUBTASK       |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 2faff3-add-configurable-start-state-and-routes-to-orchestrator             |
| Priority    | —           |
| Complexity  | —                      |
| Stop-after  | false                  |
| Last-task   | false                  |
| Level       | INTERNAL              |

## Goal

Remove the `--request` flag and the dead `is_first_run` TM bootstrap
path from the orchestrator.

## Context

The `--request` / first-run TM path became unreachable when the
orchestrator was changed to always start at `ARCHITECT`. TM is only
ever routed to from ARCHITECT or TESTER — it never starts cold. The
`is_first_run` check (`not CURRENT_JOB_FILE.exists()`) in the TM prompt
branch is therefore dead code. With `--start-state` implemented in
`d21b9d`, the cold-start path is available as an explicit opt-in, making
`--request` fully redundant. This subtask removes the flag, the dead
branch, and updates the docs accordingly.

## Components

_To be completed by the ARCHITECT._

## Design

_To be completed by the ARCHITECT._

## Acceptance Criteria

_To be completed by the ARCHITECT._

## Suggested Tools

_To be completed by the ARCHITECT._

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
