# Task: design-pm-role

| Field    | Value                                         |
|----------|-----------------------------------------------|
| Status   | backlog                                       |
| Epic     | main                                          |
| Tags     | project-management, orchestrator              |
| Parent   | 651a51-add-project-management-system-template |
| Priority | HIGH                                          |

## Description

Design the PROJECT MANAGER role for the ai-builder orchestrator pipeline.

The PROJECT MANAGER is responsible for:
- Receiving a high-level feature or project request
- Decomposing it into tasks and subtasks using `new-task.sh`
- Sequencing work and deciding what the ARCHITECT picks up next
- Tracking progress via `list-tasks.sh` and `complete-task.sh`
- Determining when a project is complete

Design deliverables:
- A `roles/PROJECT_MANAGER.md` prompt/instruction file defining the role's
  responsibilities, decision rules, tool usage, and handoff protocol to the
  ARCHITECT
- A description of how the PM interacts with the task system as shared state
  across pipeline sessions
- Decision rules for: task granularity, when to break down further vs proceed,
  how to handle TESTER failures (create a bug task vs retry)

## Documentation

Document the role in `sandbox/brainstorm-agentic-platform-builder-orchestration.md`
and in `roles/PROJECT_MANAGER.md`.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
