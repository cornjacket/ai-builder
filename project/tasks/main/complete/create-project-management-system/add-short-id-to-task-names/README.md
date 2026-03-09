# Task: add-short-id-to-task-names

| Field    | Value                            |
|----------|----------------------------------|
| Status   | in-progress                      |
| Epic     | main                             |
| Tags     | project-management, tooling      |
| Parent   | create-project-management-system |
| Priority | HIGH                             |

## Description

Prefix task directory names with a short unique ID to prevent collisions when
multiple tasks share the same human-readable name (e.g. two tasks both named
`setup-database` that end up in `complete/` at different times).

- Generate a 6-hex-character ID using `openssl rand -hex 3` (16 million
  combinations, collision-free in practice).
- Format: `<id>-<name>/` e.g. `a3f2c1-setup-database/`
- Update `new-task.sh` to generate and prepend the ID automatically. The
  `--name` flag continues to accept the human-readable portion only.
- Update all other scripts (`move-task.sh`, `complete-subtask.sh`,
  `delete-task.sh`, `restore-task.sh`, `list-tasks.sh`) to handle the
  ID-prefixed directory name transparently where needed.
- The ID is opaque — scripts should match on the full directory name, not
  parse out the ID.

## Documentation

Update `project/tasks/README.md` to document the `<id>-<name>` naming
convention and explain why IDs exist.

## Subtasks

<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
