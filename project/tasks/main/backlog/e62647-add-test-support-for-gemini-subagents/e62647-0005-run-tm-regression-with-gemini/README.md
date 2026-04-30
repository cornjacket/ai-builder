# Task: run-tm-regression-with-gemini

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | e62647-add-test-support-for-gemini-subagents             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Run a TM-mode regression (user-service recommended) using Gemini agents and
confirm that DECOMPOSE_HANDLER, LEAF_COMPLETE_HANDLER, tree traversal, and
token tracking all work correctly end-to-end.

## Context

user-service is the right choice: single-level decomposition (manageable run
time), exercises DECOMPOSE_HANDLER and LEAF_COMPLETE_HANDLER paths that
platform-monolith also uses.

Command (after subtasks 0000–0003 are complete):
```bash
tests/regression/user-service/reset.sh
python3 ai-builder/orchestrator/orchestrator.py \
    --target-repo sandbox/user-service-target \
    --output-dir  sandbox/user-service-output \
    --epic        main \
    --state-machine ai-builder/orchestrator/machines/default-gemini.json
```

Verify:
- Pipeline completes with `HANDLER_ALL_DONE`
- `run-metrics.json` has correct invocation list (ARCHITECT×N, IMPLEMENTOR×N, TESTER×N,
  DECOMPOSE_HANDLER×1, LEAF_COMPLETE_HANDLER×N)
- Internal agents (DECOMPOSE_HANDLER, LEAF_COMPLETE_HANDLER) have zero token counts
- No UNKNOWN outcomes

Record results in this subtask's Notes.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

### Run 1 (2026-03-23) — quota exhausted, ineligible

First attempt hit `TerminalQuotaError` (quota resets ~11.5h later) during the
IMPLEMENTOR invocation. Run is ineligible for comparison (`is_resumed: true`
once we resume). Resume with:

```bash
python3 ai-builder/orchestrator/orchestrator.py \
    --target-repo sandbox/user-service-target \
    --output-dir  sandbox/user-service-output \
    --epic        main \
    --state-machine ai-builder/orchestrator/machines/default-gemini.json \
    --resume
```

### Heredoc issue observed

During Run 1, the IMPLEMENTOR tried to write multi-line Go source files using
shell heredocs via `run_shell_command`. The heredoc content triggered parse
errors in Gemini's tool execution layer before the quota hit:

```
'Error node: "<" at 0:0'
'Missing node: "" at 9:22'
...
```

The errors appeared to be caused by heredoc syntax being misinterpreted by
Gemini's tool parser. Gemini was attempting constructs like:

```bash
cat <<'EOF' > store_test.go
func TestConcurrency(t *testing.T) { ... }
EOF
```

The model responsible was confirmed by inspecting `stats.models` in the result
event for the failing IMPLEMENTOR invocation:

- `gemini-3-flash-preview`: 248,121 input tokens, 10,287 output tokens, 20 tool
  calls — handled all heavy IMPLEMENTOR work including the failing heredoc writes
- `gemini-2.5-flash-lite`: ~2,800 tokens — handled only simple routing turns

The heredoc parse errors originated in `gemini-3-flash-preview`.

Watch on the next run to see if this recurs or was incidental to the quota
state. If it recurs, options to investigate:
- Pin to `gemini-2.5-flash-lite` to test if model-specific
- Use `printf`-based file writing instead of heredocs in the IMPLEMENTOR prompt
- Add a Gemini-specific note to the IMPLEMENTOR prompt about file writing style
