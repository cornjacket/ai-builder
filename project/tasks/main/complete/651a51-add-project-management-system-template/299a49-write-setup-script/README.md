# Task: write-setup-script

| Field    | Value                                         |
|----------|-----------------------------------------------|
| Status | complete |
| Epic     | main                                          |
| Tags     | project-management, tooling                   |
| Parent   | 651a51-add-project-management-system-template |
| Priority | HIGH                                          |

## Description

Write `target/setup-project.sh <target-repo-path> [--epic <name>]` that
installs the project management system into a target repository:

- Copies `target/project/` into `<target-repo-path>/project/`
- Creates the initial epic directory structure under the given epic name
  (default: `main`)
- Makes all scripts executable
- Prints a summary of what was installed and next steps
- Is idempotent — warns and exits cleanly if `project/tasks/` already exists
  in the target repo

## Documentation

Document usage in `target/SETUP.md`.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

Test scratchpad: `/Users/david/Go/src/github.com/cornjacket/ai-builder-target/`
