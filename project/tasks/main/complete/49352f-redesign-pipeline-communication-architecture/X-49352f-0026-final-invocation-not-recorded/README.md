# Task: final-invocation-not-recorded

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

Fix the ordering of directory renaming vs. document updates in the pipeline
completion sequence so that `execution_log`, `run_summary`, and the rendered
README are all written to `task.json` / `README.md` before `complete-task.sh`
renames the containing directory to `X-`.

## Root Cause (confirmed 2026-03-27)

`on-task-complete.sh` calls `complete-task.sh` on the leaf task (e.g.
`integrate`), then — when all siblings are complete — calls `complete-task.sh`
on the parent (`build-1`). `complete-task.sh` renames the directory
immediately: `build-1/` → `X-build-1/`.

Back in the orchestrator, `record_invocation` fires and adds the LCH entry to
`run.invocations`. But every subsequent write uses `top_task_json` — a `Path`
object that still points to the old `build-1/task.json`, which **no longer
exists**. `write_metrics_to_task_json` and `render_task_readme` both return
early silently. The same failure repeats in the post-loop final writes.

Consequences:
- Final LCH invocation absent from `execution_log`
- `run_summary` is `null` in task.json
- Last rendered README reflects state before the final LCH (integrate shown
  as `[ ]` even though it is complete in the file that was just renamed)

## Preferred Fix: write before rename

The correct ordering is:

1. Mark the subtask entry `complete: true` in the parent's `task.json`
   (already done by `complete-task.sh` → `json_complete_subtask`)
2. **Flush all pending orchestrator writes** — metrics, README render — while
   paths are still valid
3. **Then** rename the directory to `X-`

This means the orchestrator must perform its post-invocation writes **before**
handing off to `on-task-complete.sh`, or `on-task-complete.sh` must be split
into two phases: (a) mark complete + update task.json, (b) rename directory.

The rename is the destructive step that invalidates in-memory paths. It must
happen last.

## Alternative: deferred rename (trigger-based)

Rather than renaming directories eagerly inside `on-task-complete.sh`, the
LCH could set a `pending-rename` flag in task.json and return. The orchestrator
would flush all writes, then apply the rename as a separate post-flush step.
This keeps the rename out of the subprocess and gives the orchestrator full
control over sequencing.

## What NOT to do

Do **not** fix this by patching stale paths after the rename (e.g. checking
for `X-` prefixed variants). That treats the symptom and leaves the ordering
wrong for any future writes that might be added.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
