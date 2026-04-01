# Task: decompose-handler-component-type

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | b9529c-doc-pipeline             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Update DECOMPOSE_HANDLER to write `component_type: integrate` into the `task.json`
of the integrate subtask it creates. This is the field LCH's `route_on` reads to
route the integrate subtask directly to DOC_INTEGRATOR.

## Context

DECOMPOSE_HANDLER already sets `Level` and `Last-task` on each subtask's `task.json`.
The integrate subtask is the one whose component name is `integrate` (the last entry
in the ARCHITECT's components JSON). Add `component_type: integrate` to its `task.json`
at creation time. All other subtasks get no `component_type` field (absent = default
routing via LCH `route_on`).

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
