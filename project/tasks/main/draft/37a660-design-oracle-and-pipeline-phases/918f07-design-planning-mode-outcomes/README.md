# Subtask: design-planning-mode-outcomes

| Field    | Value                |
|----------|----------------------|
| Status   | —                    |
| Epic     | main             |
| Tags     | oracle, orchestrator, design             |
| Parent   | 37a660-design-oracle-and-pipeline-phases           |
| Priority | MED         |

## Description

Design and implement planning-mode outcomes for the ARCHITECT and TM roles,
and wire them into the orchestrator routing table.

During the Planning phase the pipeline terminates differently from the
Implementation phase — no IMPLEMENTOR or TESTER runs. The ARCHITECT and TM
need distinct outcomes to signal planning-specific states.

**Proposed new outcomes:**

| Role | Outcome | Meaning |
|---|---|---|
| ARCHITECT | `PLAN_READY` | Architecture is complete; TM can create the task tree |
| ARCHITECT | `NEEDS_REVISION` | Plan has gaps; TM has questions; iterate again |
| TM | `PLAN_READY` | Task tree created in `project/tasks/`; terminate pipeline |

**Questions to resolve:**

- Should planning outcomes be entirely separate from implementation outcomes,
  or can `DONE` be reused with the TM interpreting context from the job doc?
- How does the orchestrator know it's in Planning mode? With ROUTES moving
  toward external config, Planning mode is likely a separate ROUTES config
  file rather than a hardcoded branch — `PLAN_READY` would simply not appear
  in the implementation ROUTES config and vice versa.
- Should `NEEDS_REVISION` loop back to ARCHITECT indefinitely, or should
  there be a max iteration count? (The existing `MAX_ROLE_ITERATIONS` guard
  already handles self-routing loops — verify it covers this case.)

**Updated direction (2026-03-16):** Planning mode outcomes belong in a
Planning-mode ROUTES config, not hardcoded in `orchestrator.py`. Design
should be done in conjunction with `5e26c5-design-pipeline-mode-signalling`
and `2faff3-add-configurable-start-state-and-routes`.

**Deliverables:**

- Defined planning-mode outcomes and their routing in a config format
- Updated ARCHITECT prompt to include planning-mode outcome options when
  in Planning mode (or a separate `roles/ARCHITECT_PLAN.md`)
- Updated TM prompt to handle `PLAN_READY` termination
- Updated `ai-builder/FLOW.md` with the planning-mode routing table

## Notes

Depends on resolving the mode-signalling question (see subtask
`design-planning-mode-signalling`). May be implemented together with that
subtask.
