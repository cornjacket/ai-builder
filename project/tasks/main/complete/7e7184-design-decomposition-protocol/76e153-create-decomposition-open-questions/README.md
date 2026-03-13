# Subtask: create-decomposition-open-questions

| Field    | Value                |
|----------|----------------------|
| Status | complete |
| Epic     | main             |
| Tags     | —             |
| Parent   | 7e7184-design-decomposition-protocol           |
| Priority | —         |

## Description

Add decomposition-specific open questions to
`ai-builder/orchestrator/open-questions.md`.

Questions to capture (from brainstorm decomposition section):
- How does the TM know to start in decompose mode vs. design mode? (job
  template type, explicit `## Mode:` field, or TM instruction injected by Oracle)
- Should the component list format be markdown table (readable) or structured
  data like JSON/YAML (easier to parse)?
- How does the gold verifier for a service-level regression test work? It needs
  to verify assembled output of all components, not just one.
- How does the TM detect current tree depth and which nodes are still
  incomplete? Does `list-tasks.sh --depth N` give enough, or does the TM need
  to walk the tree differently?
- Does the task system need a `Complexity` field on task READMEs so the TM can
  distinguish atomic from composite without re-running the ARCHITECT?

## Notes

_None._
