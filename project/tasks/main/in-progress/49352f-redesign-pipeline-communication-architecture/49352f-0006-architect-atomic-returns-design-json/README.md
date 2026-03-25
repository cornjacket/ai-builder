# Task: architect-atomic-returns-design-json

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

Change ARCHITECT's atomic/design-mode response format to return design fields
in a fenced JSON block. The orchestrator stores these fields in the component's
`task.json` and inlines them into IMPLEMENTOR's prompt — IMPLEMENTOR never reads
the job doc file.

## Context

Currently ARCHITECT writes design content into README.md sections that
IMPLEMENTOR reads via file tool. This is the same disk-file dependency problem
as decompose mode, and it's the root cause of the Gemini `read_file` sandbox
bug (024459). Under the JSON-native model, design content travels through the
response channel and is stored in `task.json`.

**New response format (flat JSON — all string fields):**
```json
{
  "outcome": "ARCHITECT_DESIGN_READY",
  "handoff": "Designed store package: User struct, sync.RWMutex, CRUD ops...",
  "documents_written": true,
  "design": "## Design\nUser struct with ID, Name, Email...",
  "acceptance_criteria": "## Acceptance Criteria\n- All CRUD ops return correct status codes...",
  "test_command": "cd /path/to/output && go test ./store/..."
}
```

All fields map to strings (potentially Markdown prose). No nested structure.
The flat shape makes JSON reliability much higher for long responses.

**Changes required:**

1. **`roles/ARCHITECT.md`** — update atomic/design-mode instructions: emit JSON
   block with `design`, `acceptance_criteria`, `test_command` fields. Include
   JSON self-validation instruction.

2. **`orchestrator.py`** — after parsing ARCHITECT's JSON response, write
   `design`, `acceptance_criteria`, and `test_command` into the component's
   `task.json`. When building IMPLEMENTOR's prompt, read these fields from
   `task.json` and inline them — no file read by the agent.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
