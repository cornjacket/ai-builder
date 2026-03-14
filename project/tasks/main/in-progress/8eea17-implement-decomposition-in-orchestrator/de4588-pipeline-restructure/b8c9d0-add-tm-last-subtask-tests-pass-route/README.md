# Subtask: add-tm-last-subtask-tests-pass-route

| Field       | Value                                                                 |
|-------------|-----------------------------------------------------------------------|
| Status      | —                                                                     |
| Epic        | main                                                                  |
| Tags        | —                                                                     |
| Parent      | 8eea17-implement-decomposition-in-orchestrator/de4588-pipeline-restructure |
| Complexity  | —                                                                     |
| Stop-after  | false                                                                 |

## Description

Add the TM_LAST_SUBTASK_TESTS_PASS outcome and route to the orchestrator.

When all subtasks of a parent task are complete (subtasks-complete.sh
exits 0), TM:
1. Calls set-current-job.sh pointing to the parent task README
2. Emits TM_LAST_SUBTASK_TESTS_PASS

Route: ("TASK_MANAGER", "TM_LAST_SUBTASK_TESTS_PASS") -> "TESTER"

TESTER then reads the parent task README (Goal + Acceptance Criteria)
and runs service-level tests against the assembled output.

Add to ROUTES in orchestrator.py (TM mode only).
Update valid_outcomes for TASK_MANAGER to include TM_LAST_SUBTASK_TESTS_PASS.
Update routing.md with the new route and its purpose.
