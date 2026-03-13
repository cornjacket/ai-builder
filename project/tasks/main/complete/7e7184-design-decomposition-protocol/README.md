# Task: design-decomposition-protocol

| Field    | Value                |
|----------|----------------------|
| Status | complete |
| Epic     | main             |
| Tags     | orchestrator, architect, decomposition             |
| Parent   | —           |
| Priority | MED         |

## Description

Design and document the multi-level decomposition protocol: how the ARCHITECT
breaks composite components into atomic ones, how the TM navigates the task
tree, what new outcomes the ARCHITECT needs, and what metadata fields subtask
READMEs require.

This is pipeline-internal — it does not cover Oracle phase transitions (see
`b1c374-document-oracle-and-n-phase-model`). It covers the mechanics that
run inside a pipeline invocation when the ARCHITECT is in decompose mode.

**Source:** `sandbox/brainstorm-oracle-and-n-phase-pipeline.md` sections:
- "Multi-Level Decomposition Protocol"
- "New ARCHITECT Outcomes Needed"
- "Job Templates Per Phase Type"
- "Deterministic vs. Non-Deterministic Elements"
- Open questions #4 and #5, and the decomposition-specific questions

## Documentation

- `ai-builder/orchestrator/decomposition.md` — full protocol (update existing file)
- `ai-builder/orchestrator/open-questions.md` — add decomposition open questions

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [302db2-update-orchestrator-decomposition-doc](302db2-update-orchestrator-decomposition-doc/)
- [x] [43b45b-design-architect-decomposition-outcomes](43b45b-design-architect-decomposition-outcomes/)
- [x] [c6bbde-add-stop-after-and-complexity-to-subtask-template](c6bbde-add-stop-after-and-complexity-to-subtask-template/)
- [x] [76e153-create-decomposition-open-questions](76e153-create-decomposition-open-questions/)
<!-- subtask-list-end -->

## Notes

_None._
