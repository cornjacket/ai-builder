# Subtask: design-planning-tools-for-architect

| Field    | Value                |
|----------|----------------------|
| Status   | —                    |
| Epic     | main             |
| Tags     | oracle, orchestrator, design             |
| Parent   | 37a660-design-oracle-and-pipeline-phases           |
| Priority | MED         |

## Description

Design the set of read-only tools available to the ARCHITECT during the
Planning phase, and how they are scoped and injected.

During Planning the ARCHITECT needs broader context than during Implementation.
It should be able to read existing code, review history, and project structure
to produce a well-informed architecture. These tools are read-only and
context-gathering only — the ARCHITECT does not write code during Planning.

**Candidate planning tools:**

| Tool | Purpose |
|---|---|
| Codebase reader | Read existing source files to avoid duplication, align with conventions, understand what's already built |
| Review history | Read `project/reviews/` to factor in past decisions, known debt, and patterns to avoid |
| Project status | Read `project/status/` to understand recent history and what was completed |
| Dependency probe | Identify what the new feature depends on and what currently depends on it |
| Tech stack detection | Detect language versions, framework, test patterns, build system |

**Questions to resolve:**

- Are these tools injected via `--allowedTools` in `agent_wrapper.py`, or
  via a separate Planning-mode agent configuration?
- Should the ARCHITECT in Planning mode have unrestricted read access to the
  target repo, or should the Oracle pre-select and inject relevant context
  into the job document?
- Is there a risk of the ARCHITECT reading too much and exceeding context
  limits? Should the Oracle summarise relevant files rather than giving
  raw access?
- Should planning tools be defined in a `roles/ARCHITECT_PLAN.md` variant,
  or as a mode flag on the existing `roles/ARCHITECT.md`?

**Deliverables:**

- A defined list of planning tools with justification for each
- A decision on how tools are scoped (allowedTools vs Oracle pre-injection)
- Updated `agent_wrapper.py` or orchestrator if tool scoping changes are needed
- Updated ARCHITECT role prompt or a planning-mode variant

## Notes

Depends on `9b9d18-design-reviews-directory` (review history tool requires
a defined `project/reviews/` format).
