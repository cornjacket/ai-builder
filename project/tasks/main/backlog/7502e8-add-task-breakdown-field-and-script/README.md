# Task: add-task-breakdown-field-and-script

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | task-tooling           |
| Created     | 2026-04-05            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Add a `Breakdown:` field to task and subtask READMEs and write a
`what-needs-to-be-done.sh` script (and optionally a Claude slash command)
that prints just that field for a given task — so an operator can get
a token-cheap summary of what's needed without reading the full README.

## Context

Reading a full task README to understand what's left costs tokens and
context. A short `Breakdown:` field (2–5 bullets, written at task creation
time) captures the essential "what needs doing" in a scannable form.

**The script should accept:**
- Full task name: `7502e8-add-task-breakdown-field-and-script`
- Full subtask name: `7502e8-0001-write-script`
- Hex ID only: `7502e8` (resolve to the task)

**It should:**
1. Locate the task README in the task tree
2. Extract and print the `## Breakdown` section
3. Exit non-zero if no Breakdown section is found

**Slash command option:** a `/what` or `/task` Claude slash command that
calls the script and injects the output into the conversation, saving the
operator from pasting it manually.

**Subtasks needed:**
1. Add `Breakdown:` section to task/subtask README templates (in all
   `new-user-task.sh`, `new-user-subtask.sh`, `new-pipeline-build.sh`,
   `new-pipeline-subtask.sh` scripts)
2. Write `project/tasks/scripts/what-needs-to-be-done.sh`
3. Decide and implement slash command (or document script usage)
4. Update documentation

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
