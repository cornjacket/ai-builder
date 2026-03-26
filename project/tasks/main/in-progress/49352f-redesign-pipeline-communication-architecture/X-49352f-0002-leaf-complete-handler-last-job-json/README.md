# Task: leaf-complete-handler-last-job-json

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 49352f-redesign-pipeline-communication-architecture             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Update LEAF_COMPLETE_HANDLER to write `last-job.json` (instead of
`current-job.txt`) after each advancement, and to reference `task.json` paths
throughout rather than README paths. This subtask is the LEAF_COMPLETE_HANDLER
side of the `--job` / `last-job.json` change introduced in subtask 0001.

## Context

LEAF_COMPLETE_HANDLER currently updates `current-job.txt` on disk as the
pipeline advances through components. Subtask 0001 replaces `current-job.txt`
with `last-job.json` as the resume artifact. This subtask updates
LEAF_COMPLETE_HANDLER to match.

**LEAF_COMPLETE_HANDLER logic (unchanged in structure):**
1. Mark current component `complete: true` in parent's `task.json`
2. Scan parent `task.json` `subtasks` array for first entry with `complete: false`
3. If found: update in-memory active task path; write `last-job.json` to output dir
4. If all complete: signal `HANDLER_ALL_DONE`

**`last-job.json` format:**
```json
{"active_task": "/abs/path/to/task.json"}
```

**Frame stack:** references `task.json` paths instead of README paths. When
DECOMPOSE_HANDLER pushes a frame, it stores the parent `task.json` path as the
anchor. When LEAF_COMPLETE_HANDLER pops a frame, it restores the parent
`task.json` path as the active task.

**Dependency:** subtask 0001 (`--job` param) must be complete before this
subtask is implemented.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
