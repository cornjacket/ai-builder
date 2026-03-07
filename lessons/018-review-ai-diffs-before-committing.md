# Lesson 018 — Review AI Diffs Before Committing

**Category:** process
**Source project:** Cornjacket Platform
**Date:** 2026-02-13

## Context

AI agents produce mostly working code, but diffs can contain subtle issues: unintended deletions, wrong variable names, stale imports, or logic that looks right but isn't. The "Coding Genie" pattern recognizes that AI output requires careful review, not blind trust.

## Lesson

Always review the full diff before committing AI-generated changes. Treat AI output the same way you'd treat a junior developer's pull request — assume competence but verify correctness. A dedicated diff review step (or a separate reviewer agent) prevents treacherous changes from reaching the codebase.

## Decision Guidance

When setting up an AI-assisted workflow, add a mandatory diff review step before every commit. Consider separating the "write code" and "commit code" roles so the committer acts as a final checkpoint. The cost of reviewing is low; the cost of a bad commit compounds.

## Related Lessons

- [003](003-every-change-needs-a-task-document.md) — task doc provides context for reviewing the diff
- [016](016-commit-task-doc-before-implementation.md) — commit checkpoint before implementation
