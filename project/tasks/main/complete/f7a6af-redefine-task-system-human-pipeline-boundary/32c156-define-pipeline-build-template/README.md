# Task: define-pipeline-build-template

| Field       | Value         |
|-------------|---------------|
| Status | complete |
| Epic        | main      |
| Tags        | —      |
| Parent      | f7a6af-redefine-task-system-human-pipeline-boundary    |
| Priority    | —  |

## Goal

Define `pipeline-build-template.md` and `new-pipeline-subtask.sh` — the
template and creation script for pipeline-subtasks (build-N and pipeline-
internal nodes). Also deprecates `new-task.sh` once all three new scripts
are in place.

## Context

A **pipeline-subtask** is the orchestrator's entry point for a unit of build
work. It is authored by the Oracle or human, then handed off to the pipeline.
Once submitted, it is pipeline-owned.

Hierarchy position:
- Can live under a user-task, a user-subtask, or another pipeline-subtask
  (e.g. a component lives under a build-N; a sub-component under a composite).
- Can only contain pipeline-subtasks as children (components, integrate,
  test, etc.). No human-owned children are permitted under a pipeline node.

The pipeline-build-template contains:
- Metadata table: Status, Epic, Tags, Parent, Priority, Complexity,
  Stop-after, Last-task
- `## Goal` — what this build must produce
- `## Context` — service context passed down from the parent user-task
- `## Components` — filled by ARCHITECT (decompose mode)
- `## Design` — filled by ARCHITECT (design mode)
- `## Acceptance Criteria` — filled by ARCHITECT
- `## Suggested Tools` — filled by ARCHITECT
- `## Subtasks` — pipeline-internal component subtasks
- `## Notes`

It does NOT contain long-form human planning notes — those belong in the
parent user-task.

## Notes

_None._
