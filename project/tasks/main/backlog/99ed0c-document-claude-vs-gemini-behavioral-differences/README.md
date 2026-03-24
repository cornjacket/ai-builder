# Task: document-claude-vs-gemini-behavioral-differences

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | gemini, claude, docs, orchestrator               |
| Priority    | HIGH           |
| Next-subtask-id | 0000               |

## Goal

Formally document all known behavioural differences between Claude Code and
Gemini CLI as pipeline agents, the root cause of each difference, and the
resolution (implemented or pending). Promote findings from the sandbox
brainstorm into the `learning/` library and update `agent_wrapper.md`.

## Context

The brainstorm document capturing all known differences lives at:
[`sandbox/brainstorm-claude-vs-gemini-behavioral-differences.md`](../../../../../sandbox/brainstorm-claude-vs-gemini-behavioral-differences.md)

That document covers seven confirmed differences discovered through regression
testing:

1. **File tool cwd sandboxing** — Gemini's file tool is sandboxed to the
   launch cwd; Claude's works with absolute paths. Fix pending (inline
   content in prompts).
2. **Config file auto-loading** — Claude walks up from cwd; Gemini follows
   absolute paths in the prompt. Fixed (per-invocation GEMINI.md temp dir).
3. **Heredoc shell syntax** — Gemini's tool layer has parse errors on heredocs;
   Claude handles them fine. Fix pending (Gemini-specific IMPLEMENTOR prompt).
4. **Stream-json event format** — different key names for token counts
   (`usage` vs `stats`, `input_tokens` vs `input`). Fixed in `agent_wrapper.py`.
5. **OUTCOME: line splitting** — Gemini streams deltas that can split mid-line.
   Fixed (newline injection in `agent_wrapper.py`).
6. **Per-turn model routing** — Gemini auto-routes per turn; Claude uses one
   model per invocation. Tracked in `4f9fba-add-model-selection-to-machine-config`.
7. **CLI flags** — Gemini requires `--yolo`; Claude does not. Fixed.

The task is to graduate this from a sandbox brainstorm to formal documentation:
- One `learning/` file per distinct difference (or a single consolidated file
  if they are better understood together)
- Update `agent_wrapper.md` to reference the behavioural differences that
  affect its implementation
- Ensure all pending fixes have corresponding backlog tasks

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
