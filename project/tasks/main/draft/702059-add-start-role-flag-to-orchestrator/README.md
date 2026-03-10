# Task: add-start-role-flag-to-orchestrator

| Field    | Value                |
|----------|----------------------|
| Status   | draft           |
| Epic     | main             |
| Tags     | orchestrator, tooling             |
| Parent   | —           |
| Priority | MED         |

## Description

Add a `--start-role <ROLE>` flag to `ai-builder/orchestrator.py` that lets
the caller specify which pipeline role to start from, overriding the default.

**Use cases:**

- **Pipeline resume:** if a run halts mid-pipeline (e.g. IMPLEMENTOR times
  out), the operator can restart from that role without re-running earlier
  stages, providing the previous `execution.log` and handoff history as
  context
- **Targeted testing:** run a single role in isolation against a known job
  document to verify its behaviour (e.g. test only the TESTER role against
  a pre-implemented output)
- **Development:** iterate on a role's prompt without running the full
  pipeline each time

**Behaviour:**

- `--start-role` accepts any valid role name: `PROJECT_MANAGER`, `ARCHITECT`,
  `IMPLEMENTOR`, `TESTER`
- When provided, the pipeline starts at that role instead of the default
  (`PROJECT_MANAGER` in PM mode, `ARCHITECT` in non-PM mode)
- Must be compatible with both PM mode and non-PM mode
- Should validate that the requested role is defined in `AGENTS`
- When starting mid-pipeline, the operator is responsible for providing
  correct prior state (e.g. a pre-populated job document, prior handoff notes
  loaded from `execution.log`)

**Design questions to resolve:**

- Should `--start-role` also accept a `--handoff-file` to replay prior
  handoff history into the prompt?
- Should the orchestrator warn when `--start-role` skips stages that would
  normally have run (e.g. starting at TESTER without an ARCHITECT pass)?

## Documentation

Update `ai-builder/FLOW.md` with the new flag and resume pattern.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
