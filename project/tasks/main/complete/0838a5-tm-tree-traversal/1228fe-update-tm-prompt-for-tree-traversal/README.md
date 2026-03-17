# Task: update-tm-prompt-for-tree-traversal

| Field       | Value                        |
|-------------|------------------------------|
| Task-type   | USER-SUBTASK                 |
| Status | complete |
| Epic        | main                         |
| Tags        | orchestrator, tm             |
| Parent      | 0838a5-tm-tree-traversal     |
| Priority    | —                            |

## Goal

Update the TM prompt in `orchestrator.py` to use `advance-pipeline.sh` for
tree traversal and to pass `Level` correctly when creating component subtasks.

## Context

**ARCHITECT_DECOMPOSITION_READY branch:**
- When creating component subtasks, always use `--level INTERNAL`
- For the `integrate` component specifically, use `--level <parent-level>`
  (read the parent task's `Level` field and pass it through)

**TESTER_TESTS_PASS branch:**
- Replace the current multi-step `is-last-task.sh` + `next-subtask.sh` + Stop-after
  check with a single call to `on-task-complete.sh`
- Act on the result: `NEXT <path>` → TM_SUBTASKS_READY; `DONE` → TM_ALL_DONE;
  `STOP_AFTER` → TM_STOP_AFTER
- The TM emits an outcome — that is its only job in this branch

**General principle:** the prompt should describe intent, not procedure. Every
field read, condition check, and mechanical operation should be a script call.
The TM prompt's job is to know *which* scripts exist and *when* to call them —
not to re-implement their logic in prose.

**Constraint:** scripts are called by the TM agent, not integrated into the
orchestrator. The orchestrator must remain agnostic of the task management system.
The TM agent is the adapter between the pipeline and the task management system.

## Subtasks

<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
