# Subtask: update-orchestrator-decomposition-doc

| Field    | Value                |
|----------|----------------------|
| Status | complete |
| Epic     | main             |
| Tags     | —             |
| Parent   | 7e7184-design-decomposition-protocol           |
| Priority | —         |

## Description

Update `ai-builder/orchestrator/decomposition.md` with the full protocol from
the brainstorm. The file already exists with some content; absorb the remaining
brainstorm sections.

Content to add or verify is present:
- Decomposition as a planning sub-loop (the full nested diagram)
- Task tree structure and TM navigation (find next incomplete node, atomic vs
  composite, mark complete, move up)
- ARCHITECT component list format (the markdown table: Name, Complexity,
  Description)
- Job templates per phase type: `JOB-service-build`, `JOB-component-design`,
  `JOB-component-implement`, `JOB-component-test`
- Deterministic vs. non-deterministic elements
- README content by level (non-leaf vs. leaf README structure)
- Pipeline responsibilities table (who produces what documentation content)
- First regression test strategy (atomic-only first; composite in subsequent)

Source: "Multi-Level Decomposition Protocol" section of
`sandbox/brainstorm-oracle-and-n-phase-pipeline.md`.

## Notes

_None._
