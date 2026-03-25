# Task: bug-gemini-agent-cannot-read-job-doc

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | in-progress             |
| Epic        | main               |
| Tags        | gemini, orchestrator, bug               |
| Priority    | HIGH           |
| Next-subtask-id | 0000               |

## Goal

Fix all pipeline roles (ARCHITECT, IMPLEMENTOR) so they do not depend on the
Gemini file read tool to access job document content. Inline all required job
doc sections directly into each role's prompt via the orchestrator.

## Context

Gemini's `read_file` tool is sandboxed to the agent's temp cwd. Any attempt
to read a file at an absolute path outside that directory is rejected:

```
Path not in workspace: Attempted path "...README.md" resolves outside the
allowed workspace directories: /tmp/ai-builder-gemini-xxx
```

The orchestrator currently passes only the job doc path to ARCHITECT and
IMPLEMENTOR. Both agents attempt to open it via the file read tool — which
fails under Gemini, causing the pipeline to halt with `NEED_HELP`.

**Affected roles:**
- **ARCHITECT** — needs Goal, Context, Complexity, and Level inlined.
  Currently receives only the job doc path.
- **IMPLEMENTOR** — needs Goal, Design, Acceptance Criteria, and Test Command
  inlined. Currently receives only the job doc path.
- **TESTER** — already fixed. Test Command is extracted and inlined by the
  orchestrator. See `learning/agent-cwd-and-context-isolation.md`.

**Fix:** apply the same extract-and-inline pattern already used for TESTER
to ARCHITECT and IMPLEMENTOR. The orchestrator reads the job doc in Python,
extracts the relevant sections via regex, and inlines them directly into
the prompt. The agent never needs to call the file read tool.

**Section mapping:**
| Role | Sections to inline |
|------|--------------------|
| ARCHITECT | Goal, Context, Complexity (from task.json), Level (from task.json) |
| IMPLEMENTOR | Goal, Design, Acceptance Criteria, Test Command |

**Note on the pipeline redesign:**
Under the proposed JSON-native pipeline architecture
(`49352f-redesign-pipeline-communication-architecture`), job doc content will
live in `task.json` and the orchestrator will read it directly — eliminating
this class of bug entirely. This fix is a bridge solution for the current
architecture.

See `learning/pipeline-extract-dont-delegate.md` for the general principle.
Document findings in `ai-builder/orchestrator/gemini_compat.md` or a new
companion doc.

## Notes

Discovered during user-service Gemini regression run (2026-03-24). ARCHITECT
emitted `ARCHITECT_NEED_HELP` after failing to read the job doc via file tool.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
