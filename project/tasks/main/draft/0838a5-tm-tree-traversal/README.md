# Task: tm-tree-traversal

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | draft             |
| Epic        | main               |
| Tags        | orchestrator, tm |
| Priority    | HIGH           |

## Goal

Give the TASK_MANAGER the ability to traverse a multi-level task tree: mark
a completed leaf done, walk up to its parent, mark the parent done when all
its siblings are complete, find the next incomplete sibling at each level,
and signal `TM_ALL_DONE` only when the root task is fully done.

## Context

Currently the TM only handles a flat list of atomic components under a single
parent. Two related bugs observed in the regression test:

1. **Parent task never closed** — after `TM_ALL_DONE` the parent service task
   remains `in-progress` with all subtasks `[x]`. Nothing calls
   `complete-task.sh` on the parent.

2. **Composite decomposition unhandled** — if ARCHITECT marks a component
   `composite`, the TM has no branch for it and the pipeline breaks. A
   composite node needs to be further decomposed and its own subtasks walked
   before the composite itself can be marked complete.

Both are the same root issue: the TM has no tree-traversal logic. Full
analysis in `sandbox/brainstorm-composite-decomposition-gap.md`. The open
question "TM tree depth navigation" in `ai-builder/orchestrator/open-questions.md`
tracks the design gap.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
