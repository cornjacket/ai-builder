# Task: fix-pipeline-subtask-readme-rendering

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | orchestrator-core      |
| Next-subtask-id | 0000               |

## Goal

Fix two gaps in `render_readme.py`'s `_render_subtask` function and clean up
the pipeline-subtask template to remove dead or misleading sections.

## Context

Discovered during investigation of pipeline subtask README formatting. See
`render_readme.py` and `pipeline-build-template.md`.

**Gap 1 — `## Components` not rendered.**
For composite and TOP-level nodes, task.json contains a `components` array
(written by DECOMPOSE_HANDLER) with `name`, `complexity`, `source_dir`, and
`description` per component. This is richer than the subtask list (which only
shows names and completion status) but is not currently rendered in the README.
Fix: add a `## Components` table to `_render_subtask` when the array is
non-empty.

**Gap 2 — `## Suggested Tools` is a dead template section.**
The pipeline-subtask template includes `## Suggested Tools` with "_To be
completed by the ARCHITECT._". The ARCHITECT decompose-mode outcome description
says "Suggested Tools filled", but there is no `<suggested_tools>` XML tag in
the response format, no extraction in `_store_architect_design_fields`, and no
task.json field. Nothing ever writes to this section; nothing reads it.

**Open question before implementing Gap 2:**
Should `## Suggested Tools` exist at all? Two options:

A. **Remove it entirely.** The ARCHITECT already includes build/test commands in
   the component `description` (which becomes the child's `goal`), and
   `test_command` is captured explicitly in task.json and used by the internal
   TESTER. Suggested Tools is redundant with the description field.

B. **Formalise it.** Add a `suggested_tools` field to task.json, add a
   `<suggested_tools>` XML tag to the ARCHITECT decompose response, extract it
   in `_store_architect_design_fields`, and render it. This would give
   IMPLEMENTOR visibility into available shell tools and build commands.

Lean toward A unless there is a concrete case where IMPLEMENTOR needs tool
hints that are not already in the design or goal.

**No pipeline operation is affected by either gap** — agents receive all data
inline from task_state, not by reading the pipeline-subtask README. These are
human-readability fixes only.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
