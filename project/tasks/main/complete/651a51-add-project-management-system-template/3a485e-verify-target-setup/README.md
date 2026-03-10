# Subtask: verify-target-setup

| Field    | Value                |
|----------|----------------------|
| Status | complete |
| Epic     | main             |
| Tags     | project-management, tooling             |
| Parent   | 651a51-add-project-management-system-template           |
| Priority | HIGH         |

## Description

Write `target/verify-setup.sh <target-repo-path>` that checks whether a target
repository has been correctly set up with the project management system:

- All expected directories exist (`project/tasks/scripts/`, `project/status/`,
  and at least one epic with all six status folders)
- All scripts are present and executable
- Both `task-template.md` and `subtask-template.md` are present
- `project/tasks/README.md` exists
- `CLAUDE.md` exists and contains the task management section
- `GEMINI.md` exists and is a symlink pointing to `CLAUDE.md`
- Exits 0 and prints a summary if all checks pass; exits 1 and lists failures
  if any check fails

## Notes

Test scratchpad: `/Users/david/Go/src/github.com/cornjacket/ai-builder-target/`
