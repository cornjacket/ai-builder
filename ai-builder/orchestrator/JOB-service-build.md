# Job: <Service Title>

## Goal

<One paragraph describing the service to be built, its purpose, and the
problem it solves. Include any known constraints, tech stack, and how it
fits into the larger system.>

---

## Context

<Links to existing code, related services, architectural decisions, or
review history the ARCHITECT should factor into the decomposition.
Write "none" if not applicable.>

---

## Components

_To be completed by the ARCHITECT._

Decompose the service into its top-level components. For each component,
determine whether it is atomic (implementable in a single design +
implement + test pass) or composite (requires further decomposition).

Output the component list in exactly this format:

```markdown
| Name | Complexity | Description |
|------|------------|-------------|
| <component-name> | atomic | <one-line responsibility> |
| <component-name> | composite | <one-line responsibility — needs further decomposition> |
```

Output `COMPONENTS_READY` when the table is complete.
Output `NEEDS_REVISION` if the goal is ambiguous and needs clarification
before decomposition can proceed.
