# Subtask: create-roles-oracle-md

| Field    | Value                |
|----------|----------------------|
| Status   | —                    |
| Epic     | main             |
| Tags     | —             |
| Parent   | b1c374-document-oracle-and-n-phase-model           |
| Priority | —         |

## Description

Create `roles/ORACLE.md` defining the Oracle role.

Content to include:
- Role purpose: human-facing coordinator, never implements
- What the Oracle reads and manages (`project/tasks/`, `project/reviews/`,
  `project/status/`)
- Phase transition responsibilities (when to invoke each phase type)
- Stop-after handling: when to pause vs. automatically continue
- Discovery question template — the structured set of questions the Oracle
  uses when starting a new feature request:
    - Purpose: what problem does this solve? Who uses it?
    - Tech stack: language, framework, database, external services?
    - Interfaces: CLI, HTTP API, library, UI? Input/output formats?
    - Constraints: performance, security, existing conventions?
    - Scope: what is explicitly out of scope?
    - Success criteria: how will we know it's done?
    - Review checkpoints: which subtasks warrant human review?
- Session continuity: how Oracle reconstructs state from task system,
  reviews, and status files when a session closes

Mark as **DRAFT** — open question #1 (does Oracle need this file, or is it
fully defined by the target repo's CLAUDE.md?) is not yet resolved.

Source: "Core Architecture", "Role Definitions", and phase transition content
in `sandbox/brainstorm-oracle-and-n-phase-pipeline.md`.

## Notes

_None._
