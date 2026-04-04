# Task: fix-internal-readme-subtask-completion

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 8985d4-bug-pipeline-teardown-and-formatting             |
| Priority    | —           |
| Created     | 2026-04-03            |
| Completed | 2026-04-03 |
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

**Fixed 2026-04-03** — Added a post-LEAF_COMPLETE_HANDLER render pass in
`orchestrator.py` (lines 1057–1065): after every LCH invocation, walk the TOP
subtree and call `render_task_readme` for all non-TOP `task.json` files.
`complete-task.sh` updates their `task.json` via `json_complete_subtask` but
never re-rendered the README for pipeline tasks.

Verified via `platform-monolith` regression run — `TestSubtasksComplete` passed.
Residual gold test failures (IAM API) are code-generation quality issues tracked
under `f5f7b8-pipeline-acceptance-spec-writer`, not teardown bugs.
