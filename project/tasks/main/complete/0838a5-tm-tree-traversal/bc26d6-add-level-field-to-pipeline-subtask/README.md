# Task: add-level-field-to-pipeline-subtask

| Field       | Value                        |
|-------------|------------------------------|
| Task-type   | USER-SUBTASK                 |
| Status | complete |
| Epic        | main                         |
| Tags        | orchestrator, tm             |
| Parent      | 0838a5-tm-tree-traversal     |
| Priority    | —                            |

## Goal

Add a `Level` field to the pipeline-subtask template and `new-pipeline-subtask.sh`
so the ARCHITECT and TM know whether a task is at the root of the pipeline tree
(`TOP`) or an internal node (`INTERNAL`).

## Context

The ARCHITECT needs to know whether the `integrate` component it is designing
will produce a runnable entry point (`TOP`) or assemble sub-components into a
cohesive unit (`INTERNAL`). The TM needs the same signal to determine whether
`TM_ALL_DONE` is appropriate or a further upward walk is needed.

**Changes:**
- `pipeline-build-template.md` (both copies) — add `| Level | — |` field
- `new-pipeline-subtask.sh` (both copies) — add `--level <TOP|INTERNAL>` flag (default: `INTERNAL`)
- Oracle/human instructions — `build-N` entry points must be created with `--level TOP`

## Subtasks

<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
