# Task: optimize-decompose-handler-prompt

| Field       | Value                        |
|-------------|------------------------------|
| Task-type   | USER-TASK                    |
| Status      | backlog                      |
| Epic        | main                         |
| Tags        | orchestrator, pipeline       |
| Priority    | MED                          |

## Goal

Reduce the AI surface in `DECOMPOSE_HANDLER` by replacing bookkeeping
steps with a single `new-subtasks-from-components.sh` script. The handler
currently creates subtasks one at a time via shell calls; a structured
machine-readable component list emitted by the handler would let one script
handle all file operations, leaving only genuine AI work in the prompt.

## Context

The original `TASK_MANAGER` role had two branches: Branch A
(`ARCHITECT_DECOMPOSITION_READY`) and Branch B (`TESTER_TESTS_PASS`). The
split into `DECOMPOSE_HANDLER` and `LEAF_COMPLETE_HANDLER`
(`d05f90-split-task-manager-into-handlers`) resolved the branching problem
and eliminated Branch B entirely — `LEAF_COMPLETE_HANDLER` calls
`on-task-complete.sh` directly with no AI judgment involved.

`DECOMPOSE_HANDLER` (Branch A) still has room for improvement. It does
three things that require AI:
- Parse the Components table
- Write Goal/Context for each new subtask (contextual synthesis)
- Order components by implementation dependency (semantic reasoning)

And several things that don't:
- Derive parent relative path from the job doc path
- Read the parent Level field
- Call `new-pipeline-subtask.sh` per component
- Set `Last-task: true` and `Level` on the integrate subtask
- Call `set-current-job.sh` on the first subtask

If the handler emits a structured component list (e.g. one JSON object per
line: name, complexity, goal, context, is-last, level), a single
`new-subtasks-from-components.sh` script could handle all file operations —
reducing the handler's AI role to: parse table → decide order → emit list.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

### Deterministic operations in DECOMPOSE_HANDLER (candidates for scripting)

| Step | Operation | Script approach |
|------|-----------|-----------------|
| 1 | Derive parent rel-path from job doc path | Strip `<TARGET_REPO>/project/tasks/<epic>/in-progress/` prefix and `/README.md` suffix |
| 2 | Read parent Level field | `read-field.sh --field Level <readme>` |
| 3 | Call `new-pipeline-subtask.sh` per component | Already a script; wrap in `new-subtasks-from-components.sh` |
| 4a | Set `Last-task: true` on integrate subtask | `set-field.sh --field Last-task --value true <readme>` |
| 4b | Set `Level` on integrate subtask | `set-field.sh --field Level --value <parent-level> <readme>` |
| 5 | Call `set-current-job.sh` on first subtask | Already a script |
