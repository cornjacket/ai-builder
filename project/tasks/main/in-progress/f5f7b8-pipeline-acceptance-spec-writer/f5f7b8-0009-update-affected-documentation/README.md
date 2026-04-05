# Task: update-affected-documentation

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | f5f7b8-pipeline-acceptance-spec-writer             |
| Priority    | —           |
| Created     | 2026-04-03            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Update all documentation affected by the ACCEPTANCE_SPEC_WRITER changes.
This should be done as the final subtask, after implementation is complete
and the new pipeline behaviour is stable.

## Context

The ACCEPTANCE_SPEC_WRITER feature touches many parts of the system. Every
changed component needs its documentation updated to reflect the new stage,
new agents, and new prompt behaviour. Specifically:

- `ai-builder/orchestrator/machines/builder/README.md` — describe the new
  ACCEPTANCE_SPEC_WRITER state and where it fits in the pipeline flow
- `ai-builder/orchestrator/machines/builder/roles/ARCHITECT.md` — updated
  prompts for DECOMPOSE mode (reference acceptance-spec.md) and TOP integrate
  design mode (reconcile against acceptance-spec.md)
- `ai-builder/orchestrator/agents/builder/` — companion `.md` for the new
  ACCEPTANCE_SPEC_WRITER agent and spec coverage checker agent
- `ai-builder/orchestrator/orchestrator.md` or equivalent — note the new
  state in the pipeline sequence
- `ai-builder/docs/guidelines/` or wherever the pipeline authoring guide
  lives — explain that build specs must follow the structured API format so
  the ACCEPTANCE_SPEC_WRITER can parse them reliably
- `tests/regression/platform-monolith/build-spec.md` — verify it conforms
  to the format the ACCEPTANCE_SPEC_WRITER expects (serve as the reference
  example for other build specs)

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
