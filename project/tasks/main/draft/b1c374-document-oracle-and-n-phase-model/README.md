# Task: document-oracle-and-n-phase-model

| Field    | Value                |
|----------|----------------------|
| Status   | draft           |
| Epic     | main             |
| Tags     | oracle, documentation             |
| Parent   | —           |
| Priority | MED         |

## Description

Create the `ai-builder/oracle/` documentation directory and `roles/ORACLE.md`,
capturing all settled Oracle and N-phase model decisions from the brainstorm
`sandbox/brainstorm-oracle-and-n-phase-pipeline.md`.

The Oracle is the human-facing coordinator that sits above the pipeline. It
drives phase transitions, manages the human review loop, maintains continuity
across sessions, and submits jobs to the pipeline back-end. It never
implements directly.

The N-phase model describes the pipeline as a graph of phase invocations
(Discovery, Planning, Human Review, Implementation, Re-planning), connected
through the task system and `project/reviews/`. This task captures that model
in navigable documentation.

**Source:** `sandbox/brainstorm-oracle-and-n-phase-pipeline.md` — absorb all
settled content; move open questions to `oracle/open-questions.md`; delete
the brainstorm once fully absorbed.

## Documentation

All output is documentation:
- `ai-builder/oracle/README.md` — Oracle definition, N-phase diagram, phase index
- `ai-builder/oracle/phase-types.md` — all 6 phase types
- `roles/ORACLE.md` — Oracle role definition + discovery question template
- `ai-builder/oracle/open-questions.md` — unresolved questions from brainstorm

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [ ] [89a588-create-oracle-directory-and-readme](89a588-create-oracle-directory-and-readme/)
- [ ] [8375e8-create-oracle-phase-types-doc](8375e8-create-oracle-phase-types-doc/)
- [ ] [311b40-create-roles-oracle-md](311b40-create-roles-oracle-md/)
- [ ] [2eeba2-create-oracle-open-questions](2eeba2-create-oracle-open-questions/)
- [ ] [47a0a9-create-pending-tasks-from-brainstorm](47a0a9-create-pending-tasks-from-brainstorm/)
<!-- subtask-list-end -->

## Notes

_None._
