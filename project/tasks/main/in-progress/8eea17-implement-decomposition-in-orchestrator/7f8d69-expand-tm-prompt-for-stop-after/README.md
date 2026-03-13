# Subtask: expand-tm-prompt-for-stop-after

| Field    | Value                |
|----------|----------------------|
| Status | complete |
| Epic     | main             |
| Tags     | —             |
| Parent   | 8eea17-implement-decomposition-in-orchestrator           |
| Priority | —         |

## Description

Expand the TASK_MANAGER prompt to check the `Stop-after` field on a subtask
after it is marked complete, and signal the Oracle when it is set.

TM instructions for this case (after TESTER passes, marking a subtask done):
1. Mark the subtask complete using `complete-task.sh`
2. Read the `Stop-after` field from the completed subtask's README
3. If `Stop-after: true`:
   - Output `STOP_AFTER`
   - Include in HANDOFF: which subtask completed, what was implemented,
     TESTER results, and that Oracle intervention is required before continuing
4. If `Stop-after: false`:
   - Check backlog for next subtask
   - If found: set next job, output `JOBS_READY`
   - If none: output `ALL_DONE`

The orchestrator routes `STOP_AFTER → None`, halting the pipeline. The Oracle
reads the execution log to surface the results to the human.

## Notes

_None._
