# Subtask: design-planning-mode-outcomes

| Field    | Value                |
|----------|----------------------|
| Status   | —                    |
| Epic     | main             |
| Tags     | oracle, orchestrator, design             |
| Parent   | 37a660-design-oracle-and-pipeline-phases           |
| Priority | MED         |

## Description

Design and implement planning-mode outcomes for the ARCHITECT and PM roles,
and wire them into the orchestrator routing table.

During the Planning phase the pipeline terminates differently from the
Implementation phase — no IMPLEMENTOR or TESTER runs. The ARCHITECT and PM
need distinct outcomes to signal planning-specific states.

**Proposed new outcomes:**

| Role | Outcome | Meaning |
|---|---|---|
| ARCHITECT | `PLAN_READY` | Architecture is complete; PM can create the task tree |
| ARCHITECT | `NEEDS_REVISION` | Plan has gaps; PM has questions; iterate again |
| PM | `PLAN_READY` | Task tree created in `project/tasks/`; terminate pipeline |

**Questions to resolve:**

- Should planning outcomes be entirely separate from implementation outcomes,
  or can `DONE` be reused with the PM interpreting context from the job doc?
- How does the orchestrator know it's in Planning mode vs Implementation mode
  to route `PLAN_READY` to terminate rather than continue? Options:
  - PM instruction in the job document (Oracle crafts it per phase)
  - A `## Mode: plan | implement` field in the job document
  - A `--mode` CLI flag on the orchestrator
- Should `NEEDS_REVISION` loop back to ARCHITECT indefinitely, or should
  there be a max iteration count to prevent infinite loops?

**Deliverables:**

- Updated ROUTES table in `orchestrator.py` to handle planning-mode outcomes
- Updated ARCHITECT prompt in `build_prompt()` to include planning-mode
  outcome options when in Planning mode
- Updated PM prompt to handle `PLAN_READY` termination
- Updated `ai-builder/FLOW.md` with the planning-mode routing table

## Notes

Depends on resolving the mode-signalling question (see subtask
`design-planning-mode-signalling`). May be implemented together with that
subtask.
