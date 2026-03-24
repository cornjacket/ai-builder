# Task: document-gemini-stream-json-format

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

Run controlled Gemini experiments from `cwd=/tmp` to confirm clean startup
behavior (no spurious tool calls), and write a concise reference doc in
`sandbox/gemini-experiments/` covering: event types, text extraction format,
token field semantics, and OUTCOME: streaming split behavior.

## Context

Initial experiments (2026-03-22) confirmed the format but were run from the
repo root — Gemini loaded CLAUDE.md and spent 6 tool calls (~70K tokens) on
project setup before answering. Need to verify that `cwd=/tmp` prevents this.

Key findings already in `sandbox/gemini-experiments/brainstorm.md`:
- Text: `message` events with `role:assistant` + `delta:true`
- Tokens: `stats.input` (not `stats.input_tokens`) for non-cached input
- OUTCOME: split risk is real; newline injection fix is needed
- `--yolo` is the correct non-interactive approval flag

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
