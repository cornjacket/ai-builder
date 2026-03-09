# Task: write-claude-md-init-script

| Field    | Value                                         |
|----------|-----------------------------------------------|
| Status   | backlog                                       |
| Epic     | main                                          |
| Tags     | project-management, tooling                   |
| Parent   | 651a51-add-project-management-system-template |
| Priority | HIGH                                          |

## Description

Write `project/template/init-claude-md.sh <target-repo-path>` that initialises
the task management section in the target repo's `CLAUDE.md`:

- If `CLAUDE.md` does not exist, creates it with a full task management section
- If `CLAUDE.md` exists, appends the task management section (with a guard to
  avoid duplicating it on repeated runs)
- The injected section includes: workflow rules, scripts reference table, and a
  pointer to `project/tasks/README.md` for full documentation
- Creates `GEMINI.md` as a symlink to `CLAUDE.md` if not already present

## Documentation

Document usage in `project/template/SETUP.md`.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
