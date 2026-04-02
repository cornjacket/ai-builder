# Task: surface-retry-warnings-in-summary

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 1ffc75-investigate-doc-architect-linter-failures             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

When a linter or tester failure causes a retry, record a warning that bubbles up
to the orchestrator and appears in the final run summary. Regression gold tests
must assert on the expected retry count — if the actual count exceeds the expected,
the test fails.

## Context

Currently, POST_DOC_HANDLER_ATOMIC_FAIL and TESTER_TESTS_FAIL outcomes cause a
silent retry. The failure is visible in the execution log but nothing calls
attention to it — there is no alert in the summary, no counter, and no regression
check. A systematic first-attempt failure rate of 100% (as seen in doc-platform-
monolith) went unnoticed until manual inspection of the logs.

**Orchestrator changes:**
- Track a `warnings` list on `RunData` (or in `task.json`)
- When any role produces a `*_FAIL` outcome that routes back to the same role
  (linter fail → DOC_ARCHITECT, tester fail → IMPLEMENTOR), record a warning:
  `RETRY: <role> on <component> (reason: <outcome>)`
- Include a `## Warnings` section in the final run summary if `warnings` is
  non-empty, listing each retry with role, component, and outcome
- Also write `warnings` into `task.json` `run_summary` so it persists

**Regression gold test changes:**
- Each regression's gold test asserts a maximum expected retry count
- If `len(run_summary.warnings) > expected_max_retries`, the gold test fails
- This acts as a budget: we tolerate N retries as known/acceptable, but any
  increase beyond that is a regression signal
- Initial expected counts should be set to the current observed values (e.g.
  doc-platform-monolith = 5) so existing runs pass, but any worsening is caught

**Applies to both pipelines:**
- Doc pipeline: POST_DOC_HANDLER_ATOMIC_FAIL, POST_DOC_HANDLER_INTEGRATE_FAIL
- Builder pipeline: TESTER_TESTS_FAIL

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
