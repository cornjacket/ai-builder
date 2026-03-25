# Task: oracle-goal-context-in-task-json

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 49352f-redesign-pipeline-communication-architecture             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Update `new-pipeline-build.sh` to extract Goal and Context from the Oracle's
README prose and write them as fields in `task.json` at build creation time.
Update DECOMPOSE_HANDLER to write Goal and Context directly into child
`task.json` files rather than into README.md.

## Context

Goal and Context currently live only in README.md — prose written by the Oracle
for human readability. The orchestrator and DECOMPOSE_HANDLER parse them back
out of Markdown when needed. This is the first step toward JSON-native pipeline
state.

**Changes required:**

1. **`new-pipeline-build.sh`** — after creating the task directory, extract
   the `## Goal` and `## Context` sections from the Oracle's README.md and
   write them as `"goal"` and `"context"` string fields in `task.json`.

2. **`orchestrator.py`** — read `goal` and `context` from `task.json` rather
   than parsing them from README.md when building ARCHITECT prompts.

3. **`DECOMPOSE_HANDLER`** — write Goal and Context directly into the child's
   `task.json` rather than into the child's README.md. README.md for pipeline
   tasks becomes a generated view, not the authoritative source.

**Migration note:** existing builds created before this change won't have
`goal`/`context` in `task.json`. The orchestrator falls back to README.md
parsing for those builds until they complete.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
