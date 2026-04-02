# Task: doc-machine-json

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | b9529c-doc-pipeline             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Create `machines/doc/default.json` — the state machine for the doc pipeline.
Defines all roles, transitions, and the `route_on` config for LEAF_COMPLETE_HANDLER.

## Context

Roles and transitions (from brainstorm):

- DOC_ARCHITECT: claude agent, prompt at `machines/doc/roles/DOC_ARCHITECT.md`
  - DOC_ARCHITECT_DECOMPOSITION_READY → DECOMPOSE_HANDLER
  - DOC_ARCHITECT_ATOMIC_DONE → POST_DOC_HANDLER
  - DOC_ARCHITECT_NEED_HELP → null
- DOC_INTEGRATOR: claude agent, prompt at `machines/doc/roles/DOC_INTEGRATOR.md`
  - DOC_INTEGRATOR_DONE → POST_DOC_HANDLER
  - DOC_INTEGRATOR_NEED_HELP → null
- LEAF_COMPLETE_HANDLER: internal, impl `agents.builder.lch.LCHAgent`
  - route_on: field=component_type, default=HANDLER_SUBTASKS_READY, integrate=HANDLER_INTEGRATE_READY
  - HANDLER_SUBTASKS_READY → DOC_ARCHITECT
  - HANDLER_INTEGRATE_READY → DOC_INTEGRATOR
- DECOMPOSE_HANDLER: internal, impl `agents.builder.decompose.DecomposeAgent`
  - (standard decompose outcomes)
- POST_DOC_HANDLER: internal, impl `agents.doc.linter.MarkdownLinterAgent`
  - POST_DOC_HANDLER_ATOMIC_PASS → LEAF_COMPLETE_HANDLER
  - POST_DOC_HANDLER_ATOMIC_FAIL → DOC_ARCHITECT
  - POST_DOC_HANDLER_INTEGRATE_PASS → LEAF_COMPLETE_HANDLER
  - POST_DOC_HANDLER_INTEGRATE_FAIL → DOC_INTEGRATOR

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
