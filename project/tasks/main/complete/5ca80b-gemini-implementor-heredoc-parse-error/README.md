# Task: gemini-implementor-heredoc-parse-error

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | bug, gemini, implementor               |
| Priority    | HIGH           |
| Next-subtask-id | 0000               |

## Goal

Fix Gemini IMPLEMENTOR producing shell parse errors when writing multi-line
files using heredoc syntax. Implement a permanent `printf`-based file writing
rule via a Gemini-specific prompt addendum, so cold-start runs are correct
without relying on session memory from prior failures.

## Context

Gemini's tool execution layer misinterprets heredoc syntax (`cat <<'EOF'`),
producing errors like `'Error node: "<" at 0:0'` before the command runs.
Observed during user-service TM regression Run 1 (2026-03-23) — the IMPLEMENTOR
for the `store` component failed with 20 tool calls before the quota hit.
The model responsible was `gemini-3-flash-preview`.

In Run 2, Gemini proactively used `printf` instead — but only because the
failed run's handoff was in the session context. A cold start will not retain
this behaviour.

**Fix:** Add a `gemini_compat.py` utility module to the orchestrator. It
exposes a `gemini_role_addendum(role)` helper that returns Gemini-specific
prompt additions for a given role. `build_prompt()` in `orchestrator.py`
calls this helper when `agent == "gemini"` and appends the result to the
prompt. All future Gemini-specific prompt fixes live in `gemini_compat.py`
for isolation.

**Reference:** `sandbox/brainstorm-claude-vs-gemini-behavioral-differences.md`
(Difference 3)

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
