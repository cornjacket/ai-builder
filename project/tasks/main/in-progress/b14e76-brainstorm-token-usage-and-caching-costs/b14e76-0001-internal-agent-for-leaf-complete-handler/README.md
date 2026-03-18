# Task: internal-agent-for-leaf-complete-handler

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | b14e76-brainstorm-token-usage-and-caching-costs             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Introduce an `internal_agent` concept in the orchestrator so that when the state machine transitions to `LEAF_COMPLETE_HANDLER`, no claude subprocess is spawned. Instead, the orchestrator executes the handler logic directly in Python and produces an `AgentResult` in the same shape as a real agent response. The rest of the loop (routing, handoff appending, frame_stack, metrics) stays unchanged.

## Context

LCH is fully deterministic — it runs one shell script (`on-task-complete.sh`) and maps three possible outputs (`NEXT <path>`, `DONE`, `STOP_AFTER`) to three outcome strings. There is no AI reasoning. Every LCH invocation today costs ~30K cached tokens (the Claude Code system prompt floor) and ~15s of subprocess startup latency purely as overhead.

At platform-monolith scale: 5 LCH invocations × 30K = 150K cached tokens and ~75s saved per run. At larger scales this grows linearly with the number of leaf tasks.

## Notes

- Add a mechanism (state machine config or orchestrator code) that marks certain roles as `internal` — no agent subprocess, Python executes the work directly.
- For `LEAF_COMPLETE_HANDLER`, the internal implementation: read `current_job_path`, call `on-task-complete.sh` via `subprocess.run()`, parse stdout, return an `AgentResult` with the outcome and a minimal handoff string.
- The `AgentResult` returned must be identical in shape to what `run_agent()` returns so the main loop needs no changes.
- Token metrics for internal agents should be recorded as zero (no model invoked) so run-summary.md stays accurate.
- Design should be general enough that DECOMPOSE_HANDLER could be internalized later if desired.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
