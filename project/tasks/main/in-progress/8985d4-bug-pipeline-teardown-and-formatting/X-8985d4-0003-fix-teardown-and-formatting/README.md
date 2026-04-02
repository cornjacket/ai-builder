# Task: fix-teardown-and-formatting

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

Implement fixes for all root causes identified in subtasks 0000–0002.

## Context

All three symptoms share a single root cause in `decompose.py`: `level=TOP` was
propagated to the last child subtask (the integrate node), confusing `_find_level_top`
on resume.

**Two code changes applied:**

1. `ai-builder/orchestrator/agents/builder/decompose.py` — removed the
   `subtask_data["level"] = parent_level` line. Children no longer inherit
   `level=TOP`; they keep the `level=INTERNAL` value set by `new-pipeline-subtask.sh`.

2. `ai-builder/orchestrator/orchestrator.py` — changed `_find_level_top` to walk
   ALL the way up and return the topmost `level=TOP` match (previously returned
   on the first match). This is a defensive fix that handles existing task trees
   where subtasks already have `level=TOP`.

After fixing, re-run all three affected regressions and confirm:
- `## Run Summary` table appears in the TOP-level pipeline-subtask README
- All subtasks show `[x]` in the TOP README
- The TOP README uses the final rendered format (Outcome column, not Ended column)

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
