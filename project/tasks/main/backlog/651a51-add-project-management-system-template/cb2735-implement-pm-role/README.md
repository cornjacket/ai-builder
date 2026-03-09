# Task: implement-pm-role

| Field    | Value                                         |
|----------|-----------------------------------------------|
| Status   | backlog                                       |
| Epic     | main                                          |
| Tags     | project-management, orchestrator              |
| Parent   | 651a51-add-project-management-system-template |
| Priority | HIGH                                          |

## Description

Wire the PROJECT MANAGER role into the orchestrator pipeline.

- Add PM as the first stage in the pipeline, before ARCHITECT
- PM receives the project request, initialises the task system in the target
  repo (via setup-project.sh / init-claude-md.sh if not already present),
  decomposes work into tasks, then hands the first task to the ARCHITECT
- After TESTER signs off on a task, control returns to the PM to mark it
  complete and select the next task
- Pipeline loop continues until PM determines all tasks are complete
- Depends on: `design-pm-role`, `write-setup-script`, `write-claude-md-init-script`

## Documentation

Update `sandbox/brainstorm-agentic-platform-builder-orchestration.md` with the
new pipeline shape.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
