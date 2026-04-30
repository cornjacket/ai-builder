# Task: relocate-scripts-to-project-scripts

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 14fb29-add-work-log-mechanism             |
| Priority    | —           |
| Created     | 2026-04-30            |
| Completed | 2026-04-30 |
| Next-subtask-id | 0000               |

## Goal

Relocate the work-log helper from top-level `scripts/` to `project/scripts/`,
sibling of `project/tasks/scripts/`, under the existing `project/` umbrella
that houses the repo's own development tooling.

## Context

Top-level `scripts/` was a lazy default. `project/` is already the home for
process artifacts (`tasks/`, `status/`, `reviews/`) and their tooling
(`project/tasks/scripts/`); the work-log is in the same family. Keeping
`bootstrap/` strictly about workspace setup, and avoiding a new top-level
directory, both improve.

Touches: move three files, update path references in `CLAUDE.md` (3 spots),
`log.md` preamble, root `README.md`, `project/README.md`, and the script's
own help text and companion doc.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
