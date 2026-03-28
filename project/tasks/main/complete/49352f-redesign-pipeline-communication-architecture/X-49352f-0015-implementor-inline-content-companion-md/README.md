# Task: implementor-inline-content-companion-md

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 49352f-redesign-pipeline-communication-architecture             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Update IMPLEMENTOR to receive Design, Acceptance Criteria, and Test Command
inlined in its prompt from `task.json` (written by ARCHITECT in subtask 0004).
Add support for IMPLEMENTOR to optionally produce companion `.md` files and
signal this via `documents_written` in its JSON response.

## Context

Currently IMPLEMENTOR reads the Design section from the job doc via file tool —
the root cause of the Gemini `read_file` sandbox bug. Under the JSON-native
model, the orchestrator inlines all required content from `task.json` directly
into the prompt. IMPLEMENTOR never reads a file for job doc content.

**Prompt content inlined from `task.json`:**
- `design` — the design spec from ARCHITECT
- `acceptance_criteria` — what must pass
- `test_command` — the exact command to run (already prepended with `cd <output_dir>`)

**JSON response format:**
```json
{
  "outcome": "IMPLEMENTOR_IMPLEMENTATION_DONE",
  "handoff": "Implemented store package...",
  "documents_written": false
}
```

**Companion `.md` files — only when genuinely needed:**
IMPLEMENTOR writes companion docs only for non-obvious logic not covered by
ARCHITECT's design documentation (complex internal state, non-obvious error
handling, performance trade-offs discovered during implementation). The prompt
must be explicit: **do not create companion docs for straightforward
implementations — ARCHITECT's design docs are sufficient in most cases.**

When companion docs are written, they must use `Tags: implementation, <name>`.
DOCUMENTER runs afterward to rebuild the README index.

Include JSON self-validation instruction in the role prompt.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
