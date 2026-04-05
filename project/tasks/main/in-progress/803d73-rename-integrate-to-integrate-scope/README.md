# Task: rename-integrate-to-integrate-scope

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | in-progress             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | orchestrator-core      |
| Created     | 2026-04-04            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Change the integrate component naming convention from the fixed name `integrate`
to `integrate-<scope>` (e.g., `integrate-platform`, `integrate-iam`,
`integrate-user-service`). This makes run summaries and execution logs
unambiguous — readers can immediately see which integration step is running or
retrying without cross-referencing the task tree.

## Context

The orchestrator currently requires the final component in every decomposition
to be named exactly `integrate`. The DECOMPOSE_HANDLER checks
`comp_name == "integrate"` to set `component_type = "integrate"` in task.json
and to route output to the parent directory. The LCH and doc linter both route
on `component_type`, not the name, so they require no changes.

Fix: change both equality checks in `decompose.py` to `startswith("integrate")`.
Update the ARCHITECT and DOC_ARCHITECT role prompts to instruct the model to
use `integrate-<scope>` names. Update supporting docs.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
