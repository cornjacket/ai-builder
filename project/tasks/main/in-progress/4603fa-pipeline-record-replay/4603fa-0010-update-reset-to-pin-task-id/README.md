# Task: update-reset-to-pin-task-id

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 4603fa-pipeline-record-replay             |
| Priority    | —           |
| Created     | 2026-04-03            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Update `tests/regression/user-service/reset.sh` to accept an optional
`--task-id HEX` flag and pass it through to `new-user-task.sh`. Update
`test-replay.sh` to read `task_hex_id` from `recording.json` and pass it
to `reset.sh` before replaying, so the task directory names in the fresh
workspace match those in the recording.

## Context

`reset.sh` creates a new user task via `new-user-task.sh`. With the `--id`
flag added in 0009, passing the recorded hex ID here makes all downstream
task paths (`HEX-0000-build-1`, `HEX-0000-store`, etc.) identical to the
recording. `test-replay.sh` already loads `recording.json` for other data,
so reading `task_hex_id` from it is straightforward.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
