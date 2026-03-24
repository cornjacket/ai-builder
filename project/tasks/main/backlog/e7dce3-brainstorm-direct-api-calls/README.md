# Task: brainstorm-direct-api-calls

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Brainstorm and design what replacing the `claude` CLI subprocess with
direct Anthropic API calls would look like. Estimate the effort, identify
what Claude Code scaffolding would need to be reimplemented in Python, and
decide whether the token/latency savings justify the work.

## Context

Every AI agent invocation today spawns a `claude` subprocess. Claude Code
injects its own system prompt (~30K cached tokens) regardless of what we
ask the agent to do. This is the irreducible floor visible on every agent
invocation.

From `b14e76-brainstorm-token-usage-and-caching-costs` (Opportunity 3):

**Expected savings:** ~30K tokens × 19 AI invocations (current
platform-monolith baseline) = ~570K tokens/run (~22% of total cached).
Additionally removes per-invocation subprocess startup latency (~5–15s/inv).

**What Claude Code provides today that we would need to replicate:**
- Multi-turn tool-use loop (bash execution, file reads/writes)
- Streaming response handling (we already parse stream-json)
- Outcome parsing (`OUTCOME:` detection)
- `run_shell_command` and related tool implementations

**Key questions to answer in brainstorm:**
1. How much of the tool-use loop can be handled by the Anthropic SDK's
   built-in tool_use support vs custom Python?
2. Does removing the `claude` subprocess break any agent behaviours that
   rely on Claude Code internals (e.g. automatic file caching, session
   management)?
3. What is the realistic effort estimate — days, weeks?
4. Is there a hybrid approach (keep `claude` subprocess for ARCHITECT and
   IMPLEMENTOR, use direct API for TESTER) that captures most of the
   savings at lower risk?
5. How does this interact with the Gemini agent path — would we need a
   parallel reimplementation for Gemini?

**Reference:** `learning/agent-model-selection.md` for Claude vs Gemini
invocation differences.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
