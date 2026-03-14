# Subtask: create-decomposition-job-templates

| Field    | Value                |
|----------|----------------------|
| Status | complete |
| Epic     | main             |
| Tags     | —             |
| Parent   | 8eea17-implement-decomposition-in-orchestrator           |
| Priority | —         |

## Description

Create two new job document templates in `ai-builder/orchestrator/`:

**`JOB-service-build.md`** — used when ARCHITECT is in decompose mode:
- Goal: high-level description of the service/component to decompose
- Context: links to existing code, relevant constraints
- Required output: component table (Name | Complexity | Description)
- Outcome: `COMPONENTS_READY`

**`JOB-component-design.md`** — used when ARCHITECT is in design mode:
- Goal: description of the single atomic component to design
- Context: parent service description, how this component fits in
- Required output: Design section + Acceptance Criteria
- Outcome: `COMPONENT_READY`

Templates signal mode to the ARCHITECT via their structure — the component
table requirement in `JOB-service-build` tells the ARCHITECT it is in decompose
mode; the Design + AC requirement in `JOB-component-design` signals design mode.

The existing `JOB-TEMPLATE.md` remains for non-decomposition (direct job) use.

## Notes

These templates are consumed by the TM when creating job documents. The TM
selects the template based on the `Complexity` field of the next subtask.
