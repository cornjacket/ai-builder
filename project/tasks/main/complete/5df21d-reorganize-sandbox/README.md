# Task: reorganize-sandbox

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Next-subtask-id | 0002 |

## Goal

Reorganize `sandbox/` into a cleaner structure: brainstorm files under
`sandbox/brainstorms/`, and regression working dirs under
`sandbox/regressions/{name}/output/` and `sandbox/regressions/{name}/target/`.

## Context

Current layout scatters `{name}-output/`, `{name}-target/`, and `brainstorm-*.md`
flat in `sandbox/`. The desired layout groups everything by concern and colocates
output and target under a single regression directory — which also prepares the
ground for future record/replay (a single git repo per regression can cover both).

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-5df21d-0000-move-brainstorms](X-5df21d-0000-move-brainstorms/)
- [x] [X-5df21d-0001-restructure-regression-dirs](X-5df21d-0001-restructure-regression-dirs/)
<!-- subtask-list-end -->

## Notes

_None._
