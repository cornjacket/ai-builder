# Task: add-role-iteration-limit-to-orchestrator

| Field    | Value                |
|----------|----------------------|
| Status | complete |
| Epic     | main             |
| Tags     | orchestrator, safety             |
| Parent   | —           |
| Priority | MED         |

## Description

Add a per-role iteration counter to the orchestrator to prevent infinite loops
on self-routing outcomes (e.g. `ARCHITECT → NEEDS_REVISION → ARCHITECT`).

When a role routes back to itself the counter increments. If the count exceeds
a configurable threshold, the pipeline halts with an error and alerts the
Oracle, which surfaces the failure to the human.

**Behaviour:**
- Counter is per-role, reset when the role changes
- Threshold is a named constant (e.g. `MAX_ROLE_ITERATIONS = 3`)
- On breach: print a clear error message identifying the role, iteration count,
  and last outcome; exit with a non-zero code so the Oracle knows to intervene
- The halt message should be actionable: tell the Oracle what was attempted and
  suggest the human review the job document or role prompt

**Scope:** any self-loop in ROUTES, not just `NEEDS_REVISION`. Applies to all
current and future self-routing outcomes.

## Documentation

Update `ai-builder/orchestrator/orchestrator.md` with the iteration limit
constant and halt behaviour.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
