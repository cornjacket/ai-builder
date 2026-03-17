# Task: establish-ai-builder-documentation

| Field    | Value                          |
|----------|--------------------------------|
| Status   | draft                          |
| Epic     | main                           |
| Tags     | documentation, architecture    |
| Parent   | —                              |
| Priority | HIGH                           |
| Next-subtask-id | 0003               |
## Description

Establish a formal, version-controlled documentation structure for the
ai-builder project. Currently all design thinking lives in `/sandbox`
brainstorm files which are noisy, unstructured, and not committed to git.

This task produces official docs that are the authoritative reference for
the project's architecture, design decisions, and test strategy. Once complete,
all tasks and READMEs should reference these docs — not brainstorm files.

**Status: DRAFT — requires review before implementation begins.**

## Documentation

The output of this task is the documentation itself. Once complete, update
`CLAUDE.md` to point to the official docs index.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [ ] [f1b8a0-0000-design-documentation-structure](f1b8a0-0000-design-documentation-structure/)
- [ ] [f1b8a0-0001-create-docs-from-brainstorms](f1b8a0-0001-create-docs-from-brainstorms/)
- [ ] [f1b8a0-0002-audit-task-and-readme-references](f1b8a0-0002-audit-task-and-readme-references/)
<!-- subtask-list-end -->

## Notes

All subtasks should remain in draft until the documentation structure has been
reviewed and agreed upon.

**Open question — role of `docs/` vs. inline README hierarchy:**

The preferred documentation model is index-of-indexes: README.md files that
live near the code they describe, with higher layers more abstract and lower
layers more granular. This keeps documentation co-located with what it
describes and naturally visible to AI agents navigating the repo.

However, there is value in a consolidated `docs/` for content that is not
co-located with any specific code — specifically:

- **ADRs** (Architecture Decision Records) — decisions that span the whole
  codebase with no natural home in a subdirectory
- **Theory / principles** — foundational thinking (e.g. effective AI agent
  operation) that informs the whole project but isn't implementation
- **Human-facing reference** — consolidated reading for onboarding or review

The design decision to resolve in `7e44fc-design-documentation-structure`:
what belongs in `docs/` vs. inline README hierarchy, and whether `docs/`
content is intended primarily for humans, AI agents, or both. The current
`docs/` directory (adr/, agents/, runbooks/, services/) already exists and
its conventions are not yet documented.
