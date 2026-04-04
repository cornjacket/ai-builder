# Task: pin-replay-task-id

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | wont-do |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Created     | 2026-04-03            |
| Completed   | —                      |
| Next-subtask-id | 0004 |

## Goal

Pin the task hex ID during replay to match the recording, so `target/` can be
included in the snapshot comparison. Currently `target/` is excluded because
task directories use random hex IDs (`61857e-user-service/` in the recording
vs `c0e48c-user-service/` in the replay), making path-for-path comparison
impossible. By storing the hex ID in `recording.json` and passing it to
`new-user-task.sh` during reset, all task paths will be identical and the
full pipeline state — including task tree transitions — can be verified.

## Context

The replay regression test (`test-replay.sh`) currently excludes `target/`
from the snapshot diff, which means `complete-task.sh`, `on-task-complete.sh`,
and task tree state transitions are not tested. All hex-prefixed subtask
directories derive their prefix from the top-level user task ID, so pinning
just that one ID is sufficient to reproduce the full path structure.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [ ] [c56433-0000-store-hex-id-in-manifest](c56433-0000-store-hex-id-in-manifest/)
- [ ] [c56433-0001-add-id-flag-to-new-user-task](c56433-0001-add-id-flag-to-new-user-task/)
- [ ] [c56433-0002-update-reset-to-pin-task-id](c56433-0002-update-reset-to-pin-task-id/)
- [ ] [c56433-0003-enable-target-snapshot-comparison](c56433-0003-enable-target-snapshot-comparison/)
<!-- subtask-list-end -->

## Notes

_None._
