# Task: define-user-subtask-template

| Field       | Value         |
|-------------|---------------|
| Status | complete |
| Epic        | main      |
| Tags        | —      |
| Parent      | f7a6af-redefine-task-system-human-pipeline-boundary    |
| Priority    | —  |

## Goal

Define `user-subtask-template.md` and `new-user-subtask.sh` — the template
and creation script for human/Oracle-owned subtasks under a user-task or
another user-subtask.

## Context

A **user-subtask** is a human/Oracle-owned subtask used for planning steps,
reviews, approvals, research, or any work the human manages directly. It does
not go to the pipeline.

Hierarchy position:
- Can live under a user-task or under another user-subtask.
- Can contain further user-subtasks and/or pipeline-subtasks as children.
- Cannot appear under a pipeline-subtask — once the pipeline owns a node,
  its entire subtree is pipeline-managed.

The user-subtask-template contains:
- Metadata table: Status, Epic, Tags, Parent, Priority
- `## Goal` — what this subtask accomplishes
- `## Context` — relevant background
- `## Notes` — decisions, open questions

It does NOT contain: Components, Design, Acceptance Criteria, Suggested Tools,
Complexity, Stop-after, or Last-task — those are pipeline-subtask concerns.

## Notes

_None._
