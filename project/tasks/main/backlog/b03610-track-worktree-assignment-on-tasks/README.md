# Task: track-worktree-assignment-on-tasks

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | bootstrap              |
| Created     | 2026-04-05            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Add a `Worktree:` field to task README metadata so that each task can record
which worktree it is being worked in. Use this field in `list-tasks.sh` to
optionally filter out tasks assigned to a specific worktree (e.g. suppress
tasks assigned to `establish-regression-recordings` when listing from `main/`).

Changes required:
- Add `Worktree: —` to the metadata table in task README templates
- Update `new-user-task.sh`, `new-user-subtask.sh`, and `new-pipeline-build.sh`
  to include the field
- Add a `--worktree <name>` filter flag to `list-tasks.sh` that hides tasks
  where `Worktree:` matches the given name
- Document the field and flag in `project/tasks/README.md`

## Context

When listing outstanding tasks from `main/`, tasks that are actively being
worked in a dedicated worktree (e.g. `ccf4a4-establish-regression-recordings`
in `establish-regression-recordings/`) clutter the list with work that has
already been delegated. Filtering by worktree assignment gives a clean view
of what is actionable from main.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
