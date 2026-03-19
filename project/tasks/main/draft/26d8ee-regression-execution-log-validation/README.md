# Task: regression-execution-log-validation

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | draft             |
| Epic        | main               |
| Tags        | —               |
| Priority    | HIGH        |
| Next-subtask-id | 0000               |

## Goal

Add a structured validation layer to the regression suite that inspects the
execution log after every pipeline run and asserts the run conformed to spec:
correct role sequence, expected invocation count, no unexpected outcomes, token
counts within bounds, and no silent failures or skipped steps.

## Context

The current regression tests validate only the **output** — gold tests check
that the generated code compiles and passes its own tests. They say nothing
about **how** the pipeline ran: which roles fired, in what order, how many
times, with what outcomes, and whether token usage was within expected bounds.

This gap has caused bugs to go undetected until manual inspection:

- Internal LCH stdout parsing failure (run 11) — TESTER passed, LCH fired,
  but the orchestrator halted silently with exit code 1. The gold test would
  never catch this because the pipeline never finished.
- Token regressions — a change that accidentally re-enables handoff history
  for a role would double that role's cached tokens with no automated signal.
- Unexpected outcome strings — a role emitting an unrecognised outcome causes
  the orchestrator to halt; the gold test sees no output at all and fails with
  a confusing message unrelated to the root cause.

**What "within spec" means:**

1. **Role sequence** — roles fire in the order dictated by the state machine
   for the given task tree structure.
2. **Invocation count** — total invocations match the expected count for the
   regression scenario (e.g. platform-monolith always produces 24 invocations
   for a full run).
3. **Outcomes** — every invocation ends with a recognised outcome string; no
   `null` exits, no orchestrator halts mid-run.
4. **Internal roles emit zero tokens** — any role declared `"agent": "internal"`
   must have `tokens_in == 0` and `tokens_cached == 0` in the execution log.
5. **Token budgets** — per-role cached token totals stay within a configurable
   ceiling. Detects accidental re-introduction of handoff bloat.
6. **Run completes** — `HANDLER_ALL_DONE` is the final outcome; the Level: TOP
   README is marked complete.

**Implementation approach:**

The execution log is already written to `run-metrics.json` in the output
directory after each run. The validation layer should be a Go test (alongside
the existing gold tests) or a standalone script that:

1. Reads `run-metrics.json`
2. Asserts the above properties against a per-scenario spec file
3. Reports structured failures (role, invocation number, field, expected vs actual)

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
