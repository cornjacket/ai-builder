# Task: update-architect-prompts

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | f5f7b8-pipeline-acceptance-spec-writer             |
| Priority    | —           |
| Created     | 2026-04-04            |
| Completed | 2026-04-04 |
| Next-subtask-id | 0000               |

## Goal

Update the ARCHITECT role prompt so that DECOMPOSE mode and TOP integrate mode
both reference `acceptance-spec.md` when handling HTTP components.

## Context

Two prompt changes are needed:

1. **DECOMPOSE mode** — when writing component descriptions for HTTP components,
   require the ARCHITECT to read `acceptance-spec.md` from the output dir.
   Field names in component descriptions must match the spec exactly.

2. **TOP integrate mode** — require the ARCHITECT to read `acceptance-spec.md`
   and explicitly reconcile its acceptance criteria against every endpoint listed
   before emitting its response. Any gap must be flagged.

Both modes locate the file by convention (`<output_dir>/acceptance-spec.md`) —
no path injection by the orchestrator.

File to modify:
- `ai-builder/orchestrator/machines/builder/roles/ARCHITECT.md`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
