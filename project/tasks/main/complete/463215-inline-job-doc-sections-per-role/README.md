# Task: inline-job-doc-sections-per-role

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | orchestrator, prompts, gemini, performance               |
| Priority    | HIGH           |
| Next-subtask-id | 0000               |

## Goal

Change `build_prompt()` in `orchestrator.py` to inline the relevant sections
of the job document directly into each role's prompt, rather than passing the
file path and expecting the agent to read the file. Each role receives only the
sections it actually needs.

## Context

Currently all roles receive:
```
The shared job document is at: /absolute/path/to/README.md
```

The agent then uses a file read tool to open it. This has two problems:

**1. Gemini file tool sandboxing.** Gemini's file read tool is restricted to
its launch cwd (a temp directory). It cannot read files at absolute paths
outside that directory. This is why TESTER emitted `TESTER_NEED_HELP` during
the first TM Gemini regression — it could not open the job doc. The underlying
cause is documented in
`sandbox/brainstorm-claude-vs-gemini-behavioral-differences.md` (Difference 1).

**2. Unnecessary tool calls.** Both Claude and Gemini spend a tool call (and
tokens) reading a file the orchestrator already has open as a `Path` object.
Inlining eliminates this entirely.

### Proposed per-role section mapping

| Role | Sections to inline |
|------|--------------------|
| ARCHITECT (Design mode) | `## Goal`, `## Context` |
| ARCHITECT (Decompose mode) | `## Goal`, `## Context` |
| IMPLEMENTOR | `## Goal`, `## Design`, `## Acceptance Criteria`, `## Test Command` |

The file path should still be included for reference (agents use it for writing
output files), but the content sections remove the need for any file read.

### Implementation notes

- `build_prompt()` already receives `job_doc: Path`. Add a helper that parses
  the job doc and returns a dict of section name → content.
- Inline the appropriate sections as a fenced block or inline markdown
  immediately after the path reference.
- If a section is missing from the job doc, omit it silently (don't error) —
  ARCHITECT may not yet have written `## Design` when IMPLEMENTOR first runs
  in some edge cases.

### Related

- `sandbox/brainstorm-claude-vs-gemini-behavioral-differences.md`
- `99ed0c-document-claude-vs-gemini-behavioral-differences`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
