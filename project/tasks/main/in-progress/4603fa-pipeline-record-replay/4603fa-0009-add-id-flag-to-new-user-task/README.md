# Task: add-id-flag-to-new-user-task

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

Add an `--id HEX` flag to `new-user-task.sh` (in `target/`) that uses the
supplied 6-char hex string as the task ID instead of generating a random one.
When `--id` is absent, behavior is unchanged. The flag is optional and only
used by `reset.sh` during replay.

## Context

`new-user-task.sh` currently generates its hex ID with something like
`openssl rand -hex 3`. The `--id` flag must bypass that generation and use
the provided value directly, so the resulting directory name matches the
recording exactly.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
