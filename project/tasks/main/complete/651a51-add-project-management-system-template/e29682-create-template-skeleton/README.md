# Task: create-template-skeleton

| Field    | Value                                         |
|----------|-----------------------------------------------|
| Status | complete |
| Epic     | main                                          |
| Tags     | project-management, tooling                   |
| Parent   | 651a51-add-project-management-system-template |
| Priority | HIGH                                          |

## Description

Create the `target/` directory in ai-builder as the canonical portable skeleton.

Structure to create:
```
target/
    project/
        tasks/
            scripts/      ← copy all .sh files and task-template.md from project/tasks/scripts/
            README.md     ← generic (written by write-template-readme subtask)
        status/           ← empty, placeholder for daily status reports
```

Steps:
- Copy `project/tasks/scripts/` in full into `target/project/tasks/scripts/`
- Create empty status folders under `target/project/tasks/main/`: `inbox/`,
  `draft/`, `backlog/`, `in-progress/`, `complete/`, `wont-do/`
- The result must be `cp -r target/project/ <target-repo>/project/` ready

## Documentation

None needed beyond the target/ directory itself.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
