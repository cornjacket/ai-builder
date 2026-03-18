# Task: update-agent-result-tokens

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 51de6e-track-pipeline-build-metrics             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Extend `AgentResult` with token fields and capture them from the claude CLI's
`result` event in `agent_wrapper.py`.

- Add `tokens_in: int`, `tokens_out: int`, `tokens_cached: int` to `AgentResult`
  (default 0 so gemini and other agents are non-breaking)
- In `run_agent`, detect the `result` event (type `"result"`) emitted at end
  of a claude stream-json run. Extract `input_tokens`, `output_tokens`, and
  `cache_read_input_tokens`. Store and return in `AgentResult`.

## Context

The claude CLI emits a final JSON event of type `"result"` containing usage
stats. The agent_wrapper currently ignores it. This subtask makes token data
available to the orchestrator so metrics.py can record it per invocation.
The `result` event format: `{"type":"result","subtype":"success","usage":{"input_tokens":N,"output_tokens":N,...}}`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
