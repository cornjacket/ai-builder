# Task: create-template-skeleton

| Field    | Value                |
|----------|----------------------|
| Status   | backlog           |
| Epic     | main             |
| Tags     | project-management, tooling             |
| Parent   | 651a51-add-project-management-system-template           |
| Priority | HIGH         |

## Description

Create `project/template/` inside ai-builder as the canonical portable skeleton.
Copy the entire `project/` structure and scripts, then strip it clean:

- Copy `project/tasks/scripts/` in full (all `.sh` files and `task-template.md`)
- Create empty status folders: `inbox/`, `draft/`, `backlog/`, `in-progress/`,
  `complete/`, `wont-do/` under `tasks/<epic>/` with a placeholder epic name
- Remove all existing task content — no ai-builder-specific tasks
- Remove any ai-builder-specific references from script internals (there are none
  currently — scripts are already generic)
- The result should be a directory that can be `cp -r`'d into any repo and work
  immediately

## Documentation

Document the template location in `project/tasks/README.md`.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
