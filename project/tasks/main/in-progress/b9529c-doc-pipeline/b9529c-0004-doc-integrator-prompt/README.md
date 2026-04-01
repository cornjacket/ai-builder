# Task: doc-integrator-prompt

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

Write `machines/doc/roles/DOC_INTEGRATOR.md` — the role prompt for DOC_INTEGRATOR.
Runs only at integrate nodes after all sibling sub-components are complete.

## Context

DOC_INTEGRATOR receives the frame-scoped handoff history (compact summaries from
every completed sibling). It must:
- Write cross-component synthesis docs: `data-flow.md`, `api.md` (as applicable)
- Write or update the directory `README.md` as a meaningful overview, not a file listing
- NOT re-read individual source files — works from handoff summaries only
- Emit DOC_INTEGRATOR_DONE with a compact handoff summary of what was produced

Purpose/Tags header required on every .md file written.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
