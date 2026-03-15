# Task: update-aibuilder-claude-md-two-task-domains

| Field       | Value         |
|-------------|---------------|
| Status | complete |
| Epic        | main      |
| Tags        | —      |
| Parent      | f7a6af-redefine-task-system-human-pipeline-boundary    |
| Priority    | —  |

## Goal

Update `CLAUDE.md` (ai-builder's own) to document all three task types,
the hierarchy rules, and the two domains so the frontend AI knows which
type to use and how to behave.

## Context

The current `CLAUDE.md` describes one unified task system. After the redesign
there are three task types in two domains:

**Frontend domain** (human/Oracle-facing):
- **user-task**: top-level, long-lived, captures intent/context/decisions.
  Use `user-task-template.md`.
- **user-subtask**: human-owned subtask for planning, reviews, approvals.
  Use `user-subtask-template.md`. Does not go to the pipeline.

**Pipeline domain** (orchestrator/TM-owned):
- **pipeline-subtask** (build-N): entry point authored by Oracle, submitted
  to orchestrator. Use `pipeline-build-template.md`. Pipeline-owned once
  submitted. Pipeline-internal children are also pipeline-subtasks.

Hierarchy rules to document in CLAUDE.md:
- All top-level work must be a user-task.
- user-task can contain user-subtasks and/or pipeline-subtasks.
- user-subtask can contain user-subtasks and/or pipeline-subtasks.
- pipeline-subtask can only contain pipeline-subtasks.
- No human-owned node may appear under a pipeline-owned node.

CLAUDE.md must also make clear:
- Which template to use for each type
- That pipeline-internal subtasks must not be manually edited once submitted
- How to create a new build-N under an existing user-task
- The `project/projects/` convention for long-running multi-build services

## Notes

_None._
