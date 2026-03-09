# Task: establish-ai-builder-documentation

| Field    | Value                          |
|----------|--------------------------------|
| Status   | draft                          |
| Epic     | main                           |
| Tags     | documentation, architecture    |
| Parent   | —                              |
| Priority | HIGH                           |

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
- [ ] [7e44fc-design-documentation-structure](7e44fc-design-documentation-structure/)
- [ ] [60ae18-create-docs-from-brainstorms](60ae18-create-docs-from-brainstorms/)
- [ ] [329663-audit-task-and-readme-references](329663-audit-task-and-readme-references/)
<!-- subtask-list-end -->

## Notes

All subtasks should remain in draft until the documentation structure has been
reviewed and agreed upon.
