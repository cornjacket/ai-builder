# Task: pipeline-theory-of-operation-doc

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

Write a theory-of-operation document for the redesigned pipeline. The document
should cover:

- End-to-end flow from Oracle job submission to pipeline completion
- Role of each agent (ARCHITECT decompose mode, ARCHITECT design mode,
  IMPLEMENTOR, TESTER, DECOMPOSE_HANDLER, LEAF_COMPLETE_HANDLER) with a
  concrete walkthrough — what each agent receives, does, and emits
- How the frame stack works and what handoff_history contains at each stage
- How task.json fields (goal, context, complexity, output_dir, last-task,
  level, name) are written and consumed across agents
- How the two-tree structure (task dir tree vs output dir tree) maps to
  each other

Place the document at `ai-builder/orchestrator/theory-of-operation.md`.

## Context

The pipeline has been substantially redesigned across subtasks 0000–0018 of
the parent task. Before this redesign is complete, a theory-of-operation doc
should be written that describes how all the pieces fit together — both for
future human maintainers and to give incoming AI sessions a clear mental model.

This subtask should be done after all implementation subtasks are complete (i.e.
after 0018), or earlier if a stable enough snapshot exists to document accurately.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
