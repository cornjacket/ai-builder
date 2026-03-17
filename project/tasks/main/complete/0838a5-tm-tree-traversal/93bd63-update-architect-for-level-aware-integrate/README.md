# Task: update-architect-for-level-aware-integrate

| Field       | Value                        |
|-------------|------------------------------|
| Task-type   | USER-SUBTASK                 |
| Status | complete |
| Epic        | main                         |
| Tags        | orchestrator, architect      |
| Parent      | 0838a5-tm-tree-traversal     |
| Priority    | —                            |

## Goal

Update `ARCHITECT.md` to use the `Level` field when describing the `integrate`
component, distinguishing root-level (runnable service + e2e tests) from
internal-level (wire sub-components + component-contract tests).

## Context

Currently the integrate row description hardcodes root-level assumptions:
"Connect all components into a runnable service and verify end-to-end behaviour."
This is wrong for nested decomposition where integrate just assembles a cohesive
sub-unit that satisfies its parent composite's interface contract.

**Changes to `ARCHITECT.md`:**
- Update the integrate row description to be level-aware
- Update the explanatory text to distinguish TOP vs INTERNAL integrate behaviour:
  - `Level: TOP` → produce runnable entry point (e.g. `main.go`), e2e acceptance tests
  - `Level: INTERNAL` → assemble sub-components into cohesive unit, component-contract tests only
- The `integrate` component always inherits the Level of its parent task

## Subtasks

<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
