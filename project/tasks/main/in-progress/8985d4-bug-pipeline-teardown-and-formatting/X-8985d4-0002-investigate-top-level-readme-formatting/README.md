# Task: investigate-top-level-readme-formatting

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

Determine why the top-level pipeline-subtask README no longer appears
formatted as it did previously, and whether `render_readme.py` or
`new-pipeline-build.sh` is responsible.

## Context

Questions to answer:

1. **Is `render_readme.py` being called at all?** In the builder pipeline,
   `render_readme.py` post-processes the TOP-level README at the end of the
   run to inject the run summary and structured layout. If it is not called
   for doc/platform-monolith runs, the README would remain in its raw
   `new-pipeline-build.sh` template form.

2. **What does `new-pipeline-build.sh` generate?** Compare the initial
   template it creates against what the user-service TOP README looked like
   after a completed run. Has the template format changed?

3. **Has `render_readme.py` changed?** Check git log on `render_readme.py`
   for any recent changes that could affect output format.

4. **Is the doc machine missing a `render_readme` call?** The builder
   machine's teardown path may explicitly invoke `render_readme.py`; the
   doc machine may not. Trace the `HANDLER_ALL_DONE` path in
   `orchestrator.py` for both machines.

Expected output: identification of whether this is a missing call, a changed
template, or a changed rendering script — and whether it shares a root cause
with subtasks 0000 and 0001.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

**Same root cause as 0000. The "formatting" issue is the live-log format vs the
final rendered format.**

`render_readme.py` produces a clean final README with a `## Run Summary` table and
an `## Execution Log` table using an "Outcome" column. During a live run,
`metrics_mod.update_task_doc` maintains a different live-log table with an "Ended"
(timestamp) column.

The sequence within each loop iteration is:
1. `render_task_readme(top_task_json)` → writes final-format README (Outcome column)
2. `update_task_doc(build_readme, run)` → **overwrites** with live-format README (Ended column)

The final `render_task_readme` in the post-loop teardown is the only call that
produces the clean final view. For a run that completes normally, this post-loop
render writes the final README with Run Summary and Outcome column.

For a resumed run with the wrong `top_task_json` (due to the `level=TOP`
propagation bug), the post-loop render targets the integrate task, not doc-1/build-1.
Doc-1's README stays in the live-log format (Ended column, no Run Summary, stale
subtask list) from the end of Session 1.

`render_readme.py` is NOT the culprit — it was not changed. `new-pipeline-build.sh`
template also has not changed. The formatting difference is purely a consequence of
the resume bug leaving doc-1's README in its mid-run live-log state.
