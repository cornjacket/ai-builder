# Task: persist-active-role-for-resume

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | f5f7b8-pipeline-acceptance-spec-writer             |
| Priority    | —           |
| Created     | {{CREATED}}            |
| Completed | 2026-04-04 |
| Next-subtask-id | 0000               |

## Goal

Save the active role to `task.json` on every state transition so that
`--resume` runs can restart from the correct pipeline state rather than
always re-entering from `start_state`.

## Context

Currently `current_role = _start_state` is unconditional — the orchestrator
has no record of which role was active when a run was interrupted. Before this
change, `start_state` was always `ARCHITECT`, which happened to be correct for
any resume point. Now that `start_state` is `ACCEPTANCE_SPEC_WRITER` (a
one-shot TOP-level stage), re-entering from it on every resume is wrong.

The fix: write `"active_role": "<role>"` to the current job's `task.json` at
the start of each state transition. On `--resume`, read it back and set
`current_role` from `task.json` instead of `_start_state`.

This supersedes the idempotency workaround in `ACCEPTANCE_SPEC_WRITER.md`
(step 0 of the instructions), which should be removed once this is in place.

File to modify:
- `ai-builder/orchestrator/orchestrator.py` — write `active_role` to
  `task.json` before each agent invocation; read it on resume to set
  `current_role`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
