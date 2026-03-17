# Task: document-pipeline-behavior

| Field       | Value                        |
|-------------|------------------------------|
| Task-type   | USER-SUBTASK                 |
| Status | complete |
| Epic        | main                         |
| Tags        | orchestrator, docs           |
| Parent      | 0838a5-tm-tree-traversal     |
| Priority    | —                            |

## Goal

Write `ai-builder/orchestrator/pipeline-behavior.md` documenting the full
multi-level pipeline flow: decomposition, tree traversal, Level field semantics,
integrate behaviour at each level, and the human/pipeline boundary.

## Context

The orchestrator directory currently has `orchestrator.md` (code reference),
`routing.md` (routing table), and `open-questions.md`. There is no document
describing the pipeline's overall behaviour end-to-end — how decomposition
works recursively, how the TM walks the tree, when `TM_ALL_DONE` fires, and
what the Level field controls.

**Sections to cover:**
- Pipeline modes: flat atomic, single-level decomposition, multi-level decomposition
- The Level field: TOP vs INTERNAL, who sets it, what it controls
- Decompose Mode trigger conditions (Complexity field)
- Integrate behaviour at TOP vs INTERNAL levels
- Tree traversal algorithm (the advance-pipeline.sh loop)
- The human/pipeline boundary (Task-type check for root detection)
- Diagram of a two-level decomposition showing routing at each step

## Subtasks

<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
