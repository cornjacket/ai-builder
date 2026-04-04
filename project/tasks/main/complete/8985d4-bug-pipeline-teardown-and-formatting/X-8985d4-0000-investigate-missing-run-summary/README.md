# Task: investigate-missing-run-summary

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

Determine why the run-summary table (token counts, elapsed time) is written
to the TOP-level pipeline-subtask README in the `user-service` build
regression but is absent in `doc-user-service`, `doc-platform-monolith`, and
`platform-monolith` regressions.

## Context

Look at:
- `sandbox/user-service-output/` — TOP-level pipeline-subtask README has the
  summary table; confirm by reading it.
- `sandbox/doc-user-service-output/` and `sandbox/doc-platform-monolith-output/`
  — TOP-level pipeline-subtask README does not have the table.

Trace the code path in `orchestrator.py` that writes the summary:
- `write_metrics_to_task_json(final=True)` and `render_readme.py` are
  candidates.
- Check whether `HANDLER_ALL_DONE` triggers the same teardown path in the
  doc machine as it does in the builder machine, or whether the doc machine
  exits a different branch that skips teardown.
- Check whether `TOP_RENAME_PENDING` is involved — the builder pipeline
  renames the TOP task dir at the end; if the doc pipeline does not emit
  `TOP_RENAME_PENDING`, it may bypass the final metrics flush.

Expected output: a clear statement of which code path is skipped and why.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

**Root cause confirmed.**

`decompose.py` line 112 propagated `level=TOP` to the **last child subtask** (always
the `integrate` node) when decomposing a `level=TOP` parent:

```python
if i == len(components) - 1:
    subtask_data["last-task"] = True
    subtask_data["level"]     = parent_level   # ← BUG: copies "TOP" from parent
```

When a run is interrupted and resumed, `current-job.txt` points to
`integrate/README.md`. The orchestrator calls `_find_level_top(integrate/README.md)`,
which immediately finds `level=TOP` in the integrate's `task.json` and returns
integrate as the top-level task instead of walking up to find the real build-N entry
point.

Consequence: `top_task_json` and `build_readme` point to integrate. After
`on-task-complete.sh` calls `complete-task.sh` for integrate and renames it to
`X-integrate`, all writes to `top_task_json` fail silently (stale path). The
post-loop `write_metrics_to_task_json(final=True)` and `write_summary_to_readme`
never reach build-1/doc-1, so no `run_summary` is written and no `## Run Summary`
section appears in the TOP-level README.

This only affects runs that were interrupted and resumed. Runs that complete in a
single session work correctly because `initial_job_doc` points to build-1/doc-1
at startup, so `_find_level_top` never encounters the integrate task.

**Fix:** Remove `level=TOP` propagation in decompose.py; change `_find_level_top`
to walk to the topmost match (return last found rather than first).
