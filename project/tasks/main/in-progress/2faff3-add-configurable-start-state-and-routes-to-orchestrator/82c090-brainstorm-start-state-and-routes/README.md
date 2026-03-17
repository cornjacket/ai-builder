# Task: brainstorm-start-state-and-routes

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 2faff3-add-configurable-start-state-and-routes-to-orchestrator             |
| Priority    | —           |

## Goal

Create a brainstorm document that explores how `--start-state` and
`--routes` extraction should work. Use it as a working document for
experiments, open questions, and design notes throughout this subtask.

## Context

The orchestrator currently hardcodes two things: the starting role
(`ARCHITECT`) and the route table (`ROUTES` dict). Externalising these
makes the pipeline reusable beyond the current fixed flow. The brainstorm
should explore: CLI interface shape, JSON routes format, validation rules,
interaction between `--start-state` and TM mode, edge cases, and how
this relates to the `--request` dead-code cleanup in subtask `7a860d`.
The doc lives in `ai-builder/orchestrator/` alongside the other design
docs and is updated freely during analysis.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

Full brainstorm at `ai-builder/orchestrator/brainstorm-start-state-and-routes.md`.

Key findings:

- `--start-state` is a simple one-line substitution; validation is role-in-AGENTS plus job-doc presence check.
- `--start-state TASK_MANAGER` is out of scope — requires a third TM prompt branch that doesn't exist.
- `--routes` JSON uses full outcome names (e.g. `ARCHITECT_DESIGN_READY`), not simplified names.
- When `--routes` is provided, TM-mode route additions are NOT merged in (caller owns the full table).
- `_NEED_HELP` interception stays unconditional regardless of custom routes.
- `--request` is confirmed dead: `REQUEST` variable is defined but never consumed. Four lines to delete.
- Implementation order: remove `--request` → add `--start-state` → add `--routes` + validation → docs → regression.
