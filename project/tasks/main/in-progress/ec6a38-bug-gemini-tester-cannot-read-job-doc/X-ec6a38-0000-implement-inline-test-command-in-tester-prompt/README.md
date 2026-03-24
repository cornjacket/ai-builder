# Task: implement-inline-test-command-in-tester-prompt

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | ec6a38-bug-gemini-tester-cannot-read-job-doc             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Modify `build_prompt()` in `orchestrator.py` to extract `## Test Command`
from the job doc and inject it inline into the TESTER prompt.

## Context

Change the TESTER branch in `build_prompt()` from passing only the path:

```
The shared job document is at: <path>
```

To also inlining the Test Command section:

```
The shared job document is at: <path>

Test command:
```
<extracted command>
```
```

If `## Test Command` is absent from the job doc, omit it silently — TESTER
will fall back to `TESTER_NEED_HELP` as today.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
