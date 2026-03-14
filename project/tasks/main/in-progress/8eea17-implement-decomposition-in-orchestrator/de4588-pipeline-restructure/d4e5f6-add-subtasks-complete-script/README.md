# Subtask: add-subtasks-complete-script

| Field       | Value                                                                 |
|-------------|-----------------------------------------------------------------------|
| Status      | —                                                                     |
| Epic        | main                                                                  |
| Tags        | —                                                                     |
| Parent      | 8eea17-implement-decomposition-in-orchestrator/de4588-pipeline-restructure |
| Complexity  | —                                                                     |
| Stop-after  | false                                                                 |

## Description

Add subtasks-complete.sh to the PM scripts. Checks whether all subtasks
of a parent task are marked [x] complete in the parent README's subtask
list.

Usage:
  subtasks-complete.sh --epic <epic> --folder in-progress --parent <parent-task>

Exit codes:
  0 — all subtasks [x] (complete)
  1 — one or more subtasks [ ] remain

Used by TM after marking a subtask complete, to decide whether to emit
TM_SUBTASKS_READY (more work) or TM_LAST_SUBTASK_TESTS_PASS (escalate
to service-level testing).

Add to both project/tasks/scripts/ and target/project/tasks/scripts/.
