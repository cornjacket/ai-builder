# Subtask: update-architect-prompt-for-decomposition

| Field    | Value                |
|----------|----------------------|
| Status | complete |
| Epic     | main             |
| Tags     | —             |
| Parent   | 8eea17-implement-decomposition-in-orchestrator           |
| Priority | —         |

## Description

Update `roles/ARCHITECT.md` to describe both operating modes and the expected
output format for each.

**Decompose mode** (job template: `JOB-service-build`):
- Produce a component table: `| Name | Complexity | Description |`
- Set `Complexity: atomic` for directly implementable components
- Set `Complexity: composite` for components needing further decomposition
- Output `COMPONENTS_READY` when table is complete
- Output `NEEDS_REVISION` if the request is ambiguous and needs clarification

**Design mode** (job template: `JOB-component-design`):
- Produce a Design section and Acceptance Criteria for the single component
- Output `COMPONENT_READY` when both sections are complete
- Output `NEEDS_ARCHITECT` if implementation feedback reveals a design flaw

The ARCHITECT detects its mode from the job template structure — no explicit
mode flag is needed.

## Notes

Depends on `47412e-create-decomposition-job-templates` — the role prompt
references the template structure to explain how mode is signalled.
