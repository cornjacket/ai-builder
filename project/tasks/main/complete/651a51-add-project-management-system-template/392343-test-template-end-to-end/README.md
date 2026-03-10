# Task: test-template-end-to-end

| Field    | Value                                         |
|----------|-----------------------------------------------|
| Status | complete |
| Epic     | main                                          |
| Tags     | project-management, tooling                   |
| Parent   | 651a51-add-project-management-system-template |
| Priority | MED                                           |

## Description

End-to-end regression test of the full template installation and task
management workflow, structured like the fibonacci regression test.

Lives at `tests/regression/template-setup/` and uses `/tmp/ai-builder-target`
as the working directory (created fresh on each run).

**Test coverage:**
1. `setup-project.sh` installs correct directory structure
2. `init-claude-md.sh` creates CLAUDE.md and GEMINI.md symlink
3. Both scripts are idempotent (safe to run twice)
4. `new-task.sh` creates a task and subtask correctly
5. `list-tasks.sh` output is correct at each stage
6. `complete-task.sh --parent` marks a subtask complete
7. `move-task.sh` moves a task between status folders
8. `complete-task.sh` moves a top-level task to complete/

**Structure:**
```
tests/regression/template-setup/
    test.sh      — runs all checks, exits 0 on pass, 1 on failure
    reset.sh     — removes /tmp/ai-builder-target for a clean re-run
    README.md    — documents the test and how to run it
```

## Documentation

None needed — test is self-contained.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

Test working directory: `/tmp/ai-builder-target`
