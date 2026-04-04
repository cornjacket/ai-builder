# Task: bug-gemini-tester-cannot-read-job-doc

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | in-progress |
| Epic        | main               |
| Tags        | bug, gemini, tester               |
| Priority    | HIGH           |
| Category    | gemini-compat          |
| Next-subtask-id | 0003 |

## Goal

Fix TESTER emitting `TESTER_NEED_HELP` on every Gemini TM run because it
cannot read the job document. The orchestrator should extract `## Test Command`
from the job doc and inline it directly into the TESTER prompt so TESTER
never needs to open any file.

## Context

Gemini's file read tool is sandboxed to its launch cwd (a per-invocation temp
directory). The job doc lives in the target repo at an absolute path outside
that directory. When TESTER attempts to read it via the file tool it is
rejected:

```
I cannot access the specified job document because it is outside the
permitted workspace directory.
```

This blocks every Gemini TM regression after the first component — the
pipeline halts at the first TESTER call. Discovered during user-service
regression Run 2 (2026-03-23).

The fix belongs in `build_prompt()` in `orchestrator.py`: when building the
TESTER prompt, read the job doc (the orchestrator already has it as a `Path`)
and extract the `## Test Command` section, injecting it directly. TESTER
receives the command inline and never calls a file read tool.

This fix is correct for both Claude and Gemini — it removes an unnecessary
file read tool call regardless of agent.

**Reference:** `sandbox/brainstorm-claude-vs-gemini-behavioral-differences.md`
(Difference 1)

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-ec6a38-0000-implement-inline-test-command-in-tester-prompt](X-ec6a38-0000-implement-inline-test-command-in-tester-prompt/)
- [ ] [ec6a38-0001-gemini-pipeline-regression](ec6a38-0001-gemini-pipeline-regression/)
- [ ] [ec6a38-0002-claude-pipeline-regression](ec6a38-0002-claude-pipeline-regression/)
<!-- subtask-list-end -->

## Notes

_None._
