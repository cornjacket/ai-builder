# Task: run-fibonacci-regression-with-gemini

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | e62647-add-test-support-for-gemini-subagents             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Run the fibonacci regression using Gemini agents and confirm that token
tracking, OUTCOME: parsing, and the full ARCHITECT→IMPLEMENTOR→TESTER
sequence work correctly end-to-end.

## Context

Command (after subtasks 0000–0003 are complete):
```bash
tests/regression/fibonacci/reset.sh
python3 ai-builder/orchestrator/orchestrator.py \
    --job sandbox/fibonacci-target/project/tasks/main/in-progress/.../README.md \
    --output-dir sandbox/fibonacci-output \
    --state-machine ai-builder/orchestrator/machines/simple-gemini.json
```

Verify:
- Pipeline completes with `HANDLER_ALL_DONE` or correct terminal state
- `run-metrics.json` is written with non-zero token counts
- `tokens_cached` is plausible (Gemini uses prefix caching)
- OUTCOME: values parsed correctly — no UNKNOWN outcomes
- run-metrics shows 3 invocations (ARCHITECT, IMPLEMENTOR, TESTER)

Record results in this subtask's Notes with token totals and elapsed time.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
