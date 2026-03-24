# Task: update-orchestrator-and-internal-decompose-handler

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 829461-split-task-format-md-json-and-scripts             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Update the orchestrator to read pipeline metadata (Task-type, Level,
Complexity) from `task.json` instead of README regex, and make
DECOMPOSE_HANDLER a zero-token internal Python function.

## Context

After subtask 0001, pipeline subtasks have `task.json` for structured
metadata and a prose-only README. The orchestrator still reads Task-type,
Level, and Complexity from the README via regex — those patterns no longer
exist. Similarly, `_find_level_top` walks up the tree looking for
`| Level | TOP |` in README files, which won't be there.

DECOMPOSE_HANDLER is currently an AI agent that reads the Markdown
Components table from the parent README, creates component subtasks via
shell scripts, and fills in their metadata fields. Since Python can parse
Markdown tables reliably (unlike shell scripts with grep/sed), this role
can be made internal: zero tokens, zero latency.

The ARCHITECT still writes the Components table as Markdown in the README
(prose, AI-authored). The internal DECOMPOSE_HANDLER parses it in Python
and creates the subtasks. ARCHITECT needs to know the task Level for the
integrate component description — this is injected into the prompt by the
orchestrator (read from task.json), not read by ARCHITECT from README.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
