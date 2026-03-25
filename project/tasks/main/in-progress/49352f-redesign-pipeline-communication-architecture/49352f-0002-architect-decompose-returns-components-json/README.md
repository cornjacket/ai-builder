# Task: architect-decompose-returns-components-json

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 49352f-redesign-pipeline-communication-architecture             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Change ARCHITECT's decompose-mode response format from a `## Components`
Markdown table written to README.md to a fenced JSON block in the response
text. Update the orchestrator to parse the JSON block instead of reading and
regex-parsing README.md.

**Must be deployed atomically with subtask 0003** — deploying this alone breaks
DECOMPOSE_HANDLER.

## Context

Currently ARCHITECT writes a `## Components` table to README.md on disk.
DECOMPOSE_HANDLER reads it back and parses it with regex. This creates a
fragile disk-file dependency: a file tool failure silently breaks the pipeline,
and any table format change breaks both ARCHITECT's prompt and the regex parser.

**New response format:**
```
<prose reasoning — streams in real time>

```json
{
  "outcome": "ARCHITECT_DECOMPOSITION_READY",
  "handoff": "Decomposed user-service into 3 components...",
  "documents_written": true,
  "components": [
    {"name": "store", "complexity": "atomic", "description": "..."},
    {"name": "handlers", "complexity": "composite", "description": "..."},
    {"name": "integrate", "complexity": "atomic", "description": "..."}
  ]
}
```
```

**Changes required:**

1. **`roles/ARCHITECT.md`** — update decompose-mode instructions: emit JSON
   block instead of writing `## Components` table. Include JSON self-validation
   instruction: parse-check the JSON before returning.

2. **`orchestrator.py`** — replace `parse_outcome()` regex with a JSON block
   parser that extracts `outcome`, `handoff`, `documents_written`, and
   `components` from the fenced block.

3. **`DECOMPOSE_HANDLER` (subtask 0003)** — reads components from the parsed
   JSON response rather than from README.md. Deploy together.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
