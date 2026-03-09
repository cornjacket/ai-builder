# Task: list-tasks-respect-readme-order

| Field    | Value                |
|----------|----------------------|
| Status   | in-progress           |
| Epic     | main             |
| Tags     | project-management, tooling             |
| Parent   | create-project-management-system           |
| Priority | HIGH         |

## Description

Fix `list-tasks.sh` to read task order from the parent `README.md` instead of
using `find` (which sorts alphabetically and discards intentional ordering).

The status `README.md` is designed as a priority queue — position in the list
is meaningful (top = highest priority). Currently `list-tasks.sh` ignores this
by using `find | sort`, which alphabetises the output.

The fix should:
- Parse task names from the `<!-- task-list-start/end -->` or
  `<!-- subtask-list-start/end -->` markers in the parent README, preserving
  their order.
- Fall back to `find` only if no markers are present.
- Apply at every level of recursion (subtasks respect their parent task's
  ordering too).

This also enables `list-tasks.sh` to show checkbox state (`[ ]` vs `[x]`)
alongside each task name, making it possible to see outstanding vs completed
work at a glance without opening the parent README manually.

## Documentation

None needed beyond inline script comments.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
