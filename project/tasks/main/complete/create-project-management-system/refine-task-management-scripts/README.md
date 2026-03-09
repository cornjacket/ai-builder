# Task: refine-task-management-scripts

| Field  | Value    |
|--------|----------|
| Status | complete             |
| Epic   | main    |
| Tags   | project-management, tooling    |
| Parent | create-project-management-system  |

## Description

Refine the task management scripts based on design insights discovered during
initial implementation:

- Merge `new-task.sh` and `new-subtask.sh` into a single script. The parent
  of any task is always its containing directory — for top-level tasks this is
  the status folder, for subtasks it is the parent task directory. Both scripts
  are identical in behaviour and should be unified with an optional `--parent`
  flag.
- Add a `complete-subtask.sh` script to mark a subtask done (`[ ]` → `[x]`)
  and update the Status field in the subtask's own README. Include an `--undo`
  flag to reverse the operation.
- Add `--depth` flag to `list-tasks.sh` for recursive subtask traversal
  (default depth 1).
- Add `--root` flag to `list-tasks.sh` to specify traversal root directly
  (e.g. `--root main/draft/`) as an alternative to `--epic`/`--folder`.
- Fix the macOS `sed a\` append bug in `new-subtask.sh` (already done —
  switched to marker-based insertion).
- Update `CLAUDE.md` with workflow guideline requiring all non-sandbox work
  to be tracked in the task system.
- Add a `delete-task.sh` script to soft-delete a task or subtask: removes
  the entry from the parent README and renames the task directory by
  prepending a `.` to make it hidden. No data is lost.
- Extract the task README template from the heredoc in `new-task.sh` into
  a separate file (`project/tasks/scripts/task-template.md`). Update
  `new-task.sh` to copy and sed-substitute the template file instead of
  using a heredoc. Add a `## Documentation` section to the template to
  prompt authors to decide what needs public documentation and where.
- Add `restore-task.sh` to reverse a soft-delete: renames `.<name>` back
  to `<name>` and re-inserts the entry into the parent README.

## Subtasks

<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
