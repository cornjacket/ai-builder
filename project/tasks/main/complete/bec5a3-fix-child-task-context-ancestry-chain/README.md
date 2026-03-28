# Task: fix-child-task-context-ancestry-chain

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | orchestrator, task-management, context               |
| Priority    | HIGH           |
| Next-subtask-id | 0002 |

## Goal

Fix DECOMPOSE_HANDLER to build a structured ancestry chain in each child task's
`## Context` rather than flat-copying the parent's goal and context verbatim.

## Context

Currently DECOMPOSE_HANDLER copies the parent's `## Goal` + `## Context` into each
child's `## Context` as a flat string. At deeper nesting levels this causes duplication
— each descent re-copies all prior levels, producing repeated and increasingly
meaningless context for downstream agents.

The fix introduces a `depth` field in `task.json` (Option 2) and builds a labelled
ancestry chain instead:

```
### Level 1 — user-service
Build a user authentication service supporting OAuth2 and local login.

### Level 2 — handlers
Routes incoming HTTP requests to store and middleware.
```

Each level contributes exactly one labelled entry. Downstream ARCHITECT and IMPLEMENTOR
agents see a clean lineage without duplication.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-bec5a3-0000-implement-depth-field-and-ancestry-context](X-bec5a3-0000-implement-depth-field-and-ancestry-context/)
- [x] [X-bec5a3-0001-regression-test](X-bec5a3-0001-regression-test/)
<!-- subtask-list-end -->

## Notes

_None._
