# Subtask: design-architect-decomposition-outcomes

| Field    | Value                |
|----------|----------------------|
| Status | complete |
| Epic     | main             |
| Tags     | —             |
| Parent   | 7e7184-design-decomposition-protocol           |
| Priority | —         |

## Description

Document the new ARCHITECT outcome values for decomposition mode in
`ai-builder/orchestrator/routing.md`. The outcome set is already settled in
`decomposition.md` — this subtask updates the routing reference doc only.

Outcomes to add to routing.md:

| Outcome | Meaning |
|---------|---------|
| `COMPONENTS_READY` | Component list written; TM should create subtasks |
| `COMPONENT_READY` | Design + Acceptance Criteria complete; ready for IMPLEMENTOR |
| `NEEDS_REVISION` | Plan has gaps; iterate before task creation |

Implementation of these routes in `orchestrator.py` is tracked separately in
`implement-decomposition-in-orchestrator`.

## Notes

_None._
