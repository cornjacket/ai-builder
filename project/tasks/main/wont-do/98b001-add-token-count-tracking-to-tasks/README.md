# Task: add-token-count-tracking-to-tasks

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | wont-do |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Add `expected_token_count` and `actual_token_count` fields to every task README.
Enforce a workflow where every user task and user subtask begins with a breakdown/estimation
subtask and ends with an actual-token-count measurement subtask. Update CLAUDE.md,
target/init-claude-md.sh, and the task creation scripts to embed this discipline
into the system itself.

## Context

Token usage is currently tracked at the orchestrator level (pipeline runs) but not
for human/Oracle-driven user tasks. We need:

1. **Fields in every task README** — `expected_token_count` and `actual_token_count`
   in the metadata table so estimates and actuals are visible alongside the task.

2. **Auto-created subtasks on task creation** — when `new-user-task.sh` or
   `new-user-subtask.sh` creates a task, it should immediately inject:
   - **Subtask 0000: breakdown-and-estimate** — decompose the task into components,
     estimate total token usage to complete it, create any necessary subtasks. Only
     one level of hierarchy (no recursive decomposition).
   - **Subtask NNNN: record-actual-token-count** — final subtask (always last):
     measure and record the actual token count consumed by the whole task.

3. **CLAUDE.md reminder** — all work must be made into tasks/specs, estimated before
   starting, and measured after completion.

Backend pipeline agents estimate token usage via their role prompt instructions
(ARCHITECT.md, etc.) — not via CLAUDE.md. `target/init-claude-md.sh` generates the
customer front-end AI's CLAUDE.md and is out of scope for this task.

Open question (see sandbox/brainstorm-token-count-tracking.md): how can this be done
effectively and actually remembered? The subtask injection mechanism is the structural
answer, but there are open questions around granularity, what counts as tokens for
human-driven tasks, and whether estimates are useful when Claude drives the work.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
