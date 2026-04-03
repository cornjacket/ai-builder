# Task: fix-internal-readme-subtask-completion

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 8985d4-bug-pipeline-teardown-and-formatting             |
| Priority    | —           |
| Created     | 2026-04-03            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Fix the pipeline so that INTERNAL task READMEs correctly show `[x]` for all
child subtasks when those children complete.

## Context

Discovered during `8985d4-0007-verify-platform-monolith`. The teardown fix
in `8985d4` correctly marks subtasks `[x]` in the TOP-level task README.
But the same update is not happening at the INTERNAL level: when a child of
an INTERNAL task completes, its directory is renamed to `X-` but the parent
INTERNAL task's README still shows `- [ ]` for that subtask.

Example from the platform-monolith run:
- `X-aa9b29-0000-metrics/` contains `X-aa9b29-0000-store/`, `X-aa9b29-0001-handlers/`, `X-aa9b29-0002-integrate/`
- But `X-aa9b29-0000-metrics/README.md` shows `- [ ]` for all three

The `goldutil.CheckSubtasksComplete` test catches this. The fix must ensure
`complete-task.sh --parent` (or equivalent) updates the INTERNAL parent README
at every level, not just the TOP level.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
