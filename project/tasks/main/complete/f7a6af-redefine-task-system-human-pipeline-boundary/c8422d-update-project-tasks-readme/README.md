# Task: update-project-tasks-readme

| Field       | Value         |
|-------------|---------------|
| Status | complete |
| Epic        | main      |
| Tags        | —      |
| Parent      | f7a6af-redefine-task-system-human-pipeline-boundary    |
| Priority    | —  |

## Goal

Update `project/tasks/README.md` and `target/project/tasks/README.md` to
document the three task types, the hierarchy rules, the human/pipeline
boundary, and the three-template convention.

## Context

The current README describes a single unified task system with one template.
After this redesign there are three distinct task types with strict hierarchy
rules:

**user-task** — top-level only. All top-level work must be a user-task.
Uses `user-task-template.md`.

**user-subtask** — human/Oracle-owned subtask. Can live under a user-task
or another user-subtask. Can contain user-subtasks and/or pipeline-subtasks.
Uses `user-subtask-template.md`.

**pipeline-subtask** — pipeline entry point (build-N) or pipeline-internal
component. Can live under a user-task or user-subtask (as build-N), or under
another pipeline-subtask (as a component). Can only contain pipeline-subtasks.
Pipeline-owned once submitted. Uses `pipeline-build-template.md`.

Hierarchy rules to document:
- All top-level work must be a user-task.
- user-task can contain user-subtasks and/or pipeline-subtasks.
- user-subtask can contain user-subtasks and/or pipeline-subtasks.
- pipeline-subtask can only contain pipeline-subtasks.
- No human-owned node may appear under a pipeline-owned node.

The README update must:
- Document all three types, their ownership, and when to use each
- Document the hierarchy rules
- Describe the `project/projects/` convention for multi-build services
- Update workflow rules (which template to use when creating tasks/subtasks)
- Update script usage examples to reflect the new structure
- Cross-reference `CLAUDE.md` for the domain ownership rules

## Notes

_None._
