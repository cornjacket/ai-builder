# Task: cleanup-ai-builder-docs-structure

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | docs                   |
| Created     | 2026-04-03            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Migrate `ai-builder/docs/` contents to fit the repo documentation convention:
implementation details as `README.md` inside the directory they describe;
cross-cutting concerns under root `docs/`.

## Context

Convention established during `f00df6` (unit test CI task): `docs/` at root
is for repo-level cross-cutting concerns only. Implementation details belong
as `README.md` inside the directory they describe — not as separate `.md`
files in a parallel `docs/` tree.

`ai-builder/docs/` currently violates this:
- `task-manager.md` — Oracle operator guide for driving the pipeline. Should
  become part of `ai-builder/orchestrator/README.md` or a dedicated
  `ai-builder/orchestrator/operator-guide.md` (if it warrants its own file).
- `guidelines/documentation-standards.md` — repo-wide doc standards. Belongs
  in `docs/` at root.
- `guidelines/doc-format.md` — format spec for pipeline-generated docs.
  Belongs alongside the orchestrator or in `docs/`.

After migration, `ai-builder/docs/` should be removed entirely.

## Notes

- Low urgency — do when touching the orchestrator or docs anyway.
- Check CLAUDE.md references to `ai-builder/docs/guidelines/` before moving.
