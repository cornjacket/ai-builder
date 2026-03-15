# Task: update-target-claude-md-two-task-domains

| Field       | Value         |
|-------------|---------------|
| Status | complete |
| Epic        | main      |
| Tags        | —      |
| Parent      | f7a6af-redefine-task-system-human-pipeline-boundary    |
| Priority    | —  |

## Goal

Update `target/init-claude-md.sh` and the CLAUDE.md template it installs
in target repos to document all three task types, the hierarchy rules, and
ownership boundaries for both the frontend AI and the orchestrator/TM.

## Context

The CLAUDE.md installed in target repos is read by two different AI consumers:

**Frontend AI** (Oracle or human assistant working in the target repo):
- Creates user-tasks in `project/tasks/` using `user-task-template.md`
- Creates user-subtasks for human work using `user-subtask-template.md`
- Authors `build-N` pipeline-subtasks using `pipeline-build-template.md`
- Submits pipeline-subtasks to the orchestrator
- Must NOT edit pipeline-internal subtasks once submitted

**Orchestrator / TM** (backend pipeline agents):
- Operates on pipeline-subtasks (build-N) and their internal component children
- Fills in Components, Design, AC. Creates component subtasks. Marks them complete.
- Must NOT touch user-task or user-subtask READMEs

Hierarchy rules to document:
- All top-level work must be a user-task.
- user-task can contain user-subtasks and/or pipeline-subtasks.
- user-subtask can contain user-subtasks and/or pipeline-subtasks.
- pipeline-subtask can only contain pipeline-subtasks.
- No human-owned node may appear under a pipeline-owned node.

The updated target CLAUDE.md must also describe:
- Which template to use for each task type
- The `project/projects/` convention for long-running multi-build services
- How the Oracle hands off a pipeline-subtask to the orchestrator

## Notes

_None._
