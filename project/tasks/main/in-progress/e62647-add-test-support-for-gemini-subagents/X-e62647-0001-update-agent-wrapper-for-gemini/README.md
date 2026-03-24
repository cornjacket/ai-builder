# Task: update-agent-wrapper-for-gemini

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

Update `agent_wrapper.py` to correctly handle Gemini's stream-json format:
text extraction, token tracking, OUTCOME: split fix, and CLI command builder.

## Context

Four concrete changes required:

**1. `_extract_text`** — add Gemini assistant delta handling:
```python
if event_type == "message" and event.get("role") == "assistant" and event.get("delta"):
    return event.get("content", "")
```

**2. Token tracking** — Gemini uses `stats` not `usage`. Correct field mapping:
- `tokens_in`     ← `stats.input`          (non-cached only — NOT `stats.input_tokens` which includes cached)
- `tokens_out`    ← `stats.output_tokens`
- `tokens_cached` ← `stats.cached`

The `.gemini` scratch version incorrectly used `stats.input_tokens` (total
including cached) for `tokens_in`, making cross-agent comparisons misleading.

**3. OUTCOME: newline injection** — Gemini can end a delta mid-line with no
trailing `\n`. The next delta starting with `OUTCOME:` would accumulate as
`"...textOUTCOME: X"`, causing `^OUTCOME:` (MULTILINE) to fail. Fix: inject
`\n` before appending any chunk containing `OUTCOME:` if the previous
accumulated text doesn't end with `\n`.

**4. `_build_command`** — add Gemini case:
```python
if agent == "gemini":
    return [exe, "--output-format", "stream-json", "--yolo", "-p", prompt]
```

`cwd=Path("/tmp")` already in place — applies to Gemini the same as Claude.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
