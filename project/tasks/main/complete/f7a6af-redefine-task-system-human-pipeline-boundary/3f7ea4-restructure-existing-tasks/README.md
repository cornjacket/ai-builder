# Task: restructure-existing-tasks

| Field       | Value         |
|-------------|---------------|
| Status | wont-do |
| Epic        | main      |
| Tags        | —      |
| Parent      | f7a6af-redefine-task-system-human-pipeline-boundary    |
| Priority    | —  |

## Goal

Restructure all tasks in `draft/`, `backlog/`, and `in-progress/` to match
the three-template convention. Do not touch `complete/`.

## Context

Currently all tasks use a single template. After this redesign there are three
task types with strict hierarchy rules:

- All top-level work is a **user-task** → migrate to `user-task-template.md`.
  Remove pipeline sections (Components, Design, AC, Suggested Tools,
  Complexity, Stop-after, Last-task) if present.
- Human-owned subtasks (reviews, decisions, research, planning steps) are
  **user-subtasks** → migrate to `user-subtask-template.md`. Remove pipeline
  sections.
- Subtasks with pipeline build content (Components, Design, AC) are
  **pipeline-subtasks** → extract into a `build-1/` subdirectory using
  `pipeline-build-template.md`. The parent task becomes a user-task.

Hierarchy rules to enforce during restructure:
- user-task can contain user-subtasks and/or pipeline-subtasks.
- user-subtask can contain user-subtasks and/or pipeline-subtasks.
- pipeline-subtask can only contain pipeline-subtasks.

Scope:
- `project/tasks/main/draft/`
- `project/tasks/main/backlog/`
- `project/tasks/main/in-progress/`

Do NOT touch `project/tasks/main/complete/` — historical record.

## Notes

_None._
