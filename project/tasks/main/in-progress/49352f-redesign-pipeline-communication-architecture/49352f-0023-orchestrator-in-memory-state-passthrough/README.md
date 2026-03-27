# Task: orchestrator-in-memory-state-passthrough

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

Refactor the orchestrator to pass state between pipeline stages as in-memory
variables rather than re-reading from `task.json`. `task.json` is written for
persistence/resume only — never read during normal operation.

## Context

**Current (wrong) behaviour:** the orchestrator parses ARCHITECT's JSON
response, writes fields (`design`, `acceptance_criteria`, `test_command`, etc.)
to `task.json`, then immediately re-reads them from `task.json` when building
the next agent's prompt. The values were never out of memory — the round-trip
through disk is unnecessary.

**Design principle:**
- **Write** to `task.json` before every state transition — persistence only
- **Read** from `task.json` only on resume — restoring in-memory state after
  interruption
- **Under normal operation** — pass state directly between stages as in-memory
  variables

**Correct flow:**
```
ARCHITECT returns JSON
  → orchestrator parses: test_command, design, etc. → stored in memory
  → orchestrator writes fields to task.json (persistence)

Next stage (TESTER, IMPLEMENTOR, etc.)
  → orchestrator passes values directly from memory

Pipeline interrupted → resume
  → orchestrator reads task.json to restore in-memory state
  → proceeds as normal
```

**Affected stages:** TESTER (test_command), IMPLEMENTOR (design,
acceptance_criteria, test_command), and any other stage that currently
re-reads from task.json what the orchestrator already has in memory.

Note: subtask 0016 (TESTER internal handler) follows this principle for
TESTER. This subtask extends it to the rest of the orchestrator.

**Applies to current-job.txt too:** DECOMPOSE_HANDLER and LCH write
`current-job.txt` for persistence/resume, but the orchestrator should advance
`job_doc` in memory directly rather than re-reading the file after each handler.
`current-job.txt` is only read on `--resume` to restore the cursor after an
interrupted run.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
