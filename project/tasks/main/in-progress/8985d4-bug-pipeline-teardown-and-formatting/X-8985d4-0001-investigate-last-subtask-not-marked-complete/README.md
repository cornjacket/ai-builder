# Task: investigate-last-subtask-not-marked-complete

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 8985d4-bug-pipeline-teardown-and-formatting             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Determine why the final pipeline-subtask directory is renamed with `X-`
but its `README.md` `Status` field and the parent's subtask list entry
are not updated to `complete` / `[x]`.

## Context

In the affected regressions, `on-task-complete.sh` or `advance-pipeline.sh`
renames the directory (applies `X-` prefix) but the document-update step
does not complete. This is consistent with the orchestrator calling
`sys.exit(0)` (or equivalent) after the rename but before `complete-task.sh`
finishes writing the README.

Specifically investigate:
- The sequence inside `on-task-complete.sh`: does it rename first, then update
  the README, and could the process be interrupted between these two steps?
- Whether `LCHAgent` or the orchestrator tears down the process before
  `on-task-complete.sh` fully finishes when `HANDLER_ALL_DONE` is emitted.
- Whether this only affects the very last task (the TOP-level one) or also
  intermediate tasks — check a middle subtask README in the affected runs.
- Whether the `TOP_RENAME_PENDING` mechanism (which defers the TOP dir rename
  so metrics can be flushed first) is working correctly or being skipped for
  doc/platform-monolith pipelines.

Expected output: confirmation of the exact line/script where execution stops
prematurely, and whether this is the same root cause as the missing summary
table (subtask 0000).

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

**Same root cause as 0000.**

In Session 2 (resumed), `top_task_json = integrate/task.json` (wrong, due to
`level=TOP` propagation). After `complete-task.sh` renames `integrate` →
`X-integrate`, the path is stale. `render_task_readme(top_task_json)` is called
after every invocation — but it renders the integrate README, not the build-1/doc-1
README. So the doc-1 README's subtask list entry `[ ] ccafc6-0001-integrate` is
never re-rendered to `[x]`.

The directory IS renamed (X- prefix applied by `complete-task.sh`), and the
task.json subtask list shows `complete: true`. Only the rendered README is stale.

The symptom that the LAST subtask is not marked complete (rather than a middle one)
is explained by the resume pattern: the crash always happens after a `HANDLER_INTEGRATE_READY`
outcome (when the rate limit or PATH error hit), leaving `current-job.txt` pointing to
the root-level integrate task, which then becomes the wrong `top_task_json` on resume.
