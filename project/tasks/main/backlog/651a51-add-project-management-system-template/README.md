# Task: add-project-management-system-template

| Field    | Value                |
|----------|----------------------|
| Status   | backlog           |
| Epic     | main             |
| Tags     | project-management, orchestrator, tooling             |
| Parent   | —           |
| Priority | HIGH         |

## Description

Create a portable, self-contained project management system template that can
be dropped into any target application repository — including those generated
by the ai-builder orchestrator. The template is a first-class artifact: task
files live inside the same repo as the application they describe, making them
readable by both human developers and AI agents working in that repo.

### Approach

Copy the entire `project/` directory from ai-builder and strip it to a clean
skeleton:

- Keep the full directory structure (`tasks/<epic>/<status>/`) and all scripts
  (`scripts/*.sh`, `scripts/task-template.md`)
- Remove all existing tasks (empty out the status folders)
- Update `README.md` to be target-application-agnostic
- Add a `SETUP.md` explaining how to drop the template into a new repo

The result is a `project/` template directory that can be `cp -r`'d into any
repo and immediately used with no modification.

### Orchestrator integration

The ai-builder orchestrator should gain a **PROJECT MANAGER** role that owns
the task system in the target application repo. The PROJECT MANAGER:

- Decomposes a high-level feature request into tasks and subtasks using
  `new-task.sh`
- Sequences work and drives the ARCHITECT → IMPLEMENTOR → TESTER pipeline
  task by task
- Marks tasks complete via `complete-task.sh` when the TESTER signs off
- Maintains the task system as the shared state between all pipeline roles

The task system becomes the **persistent memory** of the pipeline — enabling
multi-session, multi-task projects rather than single-shot code generation.

## Documentation

- Add `project/template/` directory with a `SETUP.md`
- Document the PROJECT MANAGER role in `sandbox/brainstorm-agentic-platform-builder-orchestration.md`
- Add PROJECT MANAGER to the orchestrator role descriptions

## Notes

The existing `project/tasks/` system in ai-builder itself is the reference
implementation. The template is derived from it, not a parallel design.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
