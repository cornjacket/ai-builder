# Task: enable-target-snapshot-comparison

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

Remove `--exclude target` from the `compare_snapshot.py` invocation in
`test-replay.sh`. With task IDs pinned (subtasks 0008–0010), `target/`
paths are identical between recording and replay, so the snapshot diff can
include them. Also remove the `--exclude` entries for orchestrator
coordination files (`current-job.txt`, `last-job.json`, `handoff-state.json`)
from the snapshot comparison — those files live in `output/` not `target/`,
and excluding them from the diff is still correct; only `target/` changes.

Re-record the user-service recording after the pinned-ID changes are in place
(since the old recording used a random ID and its `recording.json` lacks
`task_hex_id`), then verify `test-replay.sh` passes with `target/` included.

## Context

This is the payoff subtask: once `target/` is included in the diff, task
tree state transitions (subtask completion, X- renames, etc.) are verified
by the regression test, closing the gap identified after the initial
implementation.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
