# Task: add-rename-task-script

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | task-management        |
| Priority    | LOW                    |

## Goal

Add a `rename-task.sh` script (and a matching `rename-subtask.sh`) that renames
a task or subtask in place: renames the directory, updates the `# Task:` heading
in its README, and updates the display name in the parent's subtask list.

## Context

There is currently no way to rename a task without manually editing the README
heading and the parent's subtask list entry. This gap was discovered when
renaming `51315c-minimize-ai-in-tm-prompt` to `51315c-analyze-tm-prompt-for-ai-reduction`.

The task system has three task types, each with slightly different rename
requirements:

- **USER-TASK** (top-level, no parent): rename directory + update README heading
  + update the folder-level `README.md` index.
- **USER-SUBTASK** and **PIPELINE-SUBTASK** (have a parent): rename directory
  + update README heading + update the parent task's subtask list entry.

The rename must preserve the ID prefix (e.g. `697e5a-`) — only the slug
after the hyphen changes.

Both scripts should live in `project/tasks/scripts/` and be copied to
`target/project/tasks/scripts/` as part of the same task. Documentation
companion `.md` files and README index updates are also required.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
