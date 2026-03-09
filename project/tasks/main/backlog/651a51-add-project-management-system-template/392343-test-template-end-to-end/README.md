# Task: test-template-end-to-end

| Field    | Value                                         |
|----------|-----------------------------------------------|
| Status   | backlog                                       |
| Epic     | main                                          |
| Tags     | project-management, tooling                   |
| Parent   | 651a51-add-project-management-system-template |
| Priority | MED                                           |

## Description

End-to-end test of the full template installation and usage flow:

1. Create a fresh temporary directory simulating a new target repo
2. Run `setup-project.sh` and verify the directory structure is correct
3. Run `init-claude-md.sh` and verify CLAUDE.md and GEMINI.md symlink are created
4. Run `init-claude-md.sh` again and verify it is idempotent (no duplication)
5. Create a task, a subtask, complete the subtask, move the task to complete
6. Verify `list-tasks.sh` output is correct at each step
7. Clean up the temp directory

All steps should be scripted in a `test-setup.sh` so the test is repeatable.

## Documentation

None needed — test is self-contained.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
