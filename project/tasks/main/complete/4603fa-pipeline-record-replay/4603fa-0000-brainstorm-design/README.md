# Task: brainstorm-design

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | wont-do |
| Epic        | main               |
| Tags        | —               |
| Parent      | 4603fa-pipeline-record-replay             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Complete the design brainstorm for record/replay, resolving all open questions
before any implementation subtasks are written.

## Context

An initial brainstorm is already in progress at:
`sandbox/brainstorms/brainstorm-pipeline-stop-and-replay.md`

Open questions to resolve:
- Where to commit per-invocation snapshots (target, output, or both) — walk
  through what each role writes to each directory to decide
- Single git repo per regression (output + target together) or two separate repos
- Whether replay is a flag on orchestrator.py or a separate script
- How replay detects prompt drift and invalidates a stale recording
- Stop command design: how to halt the pipeline mid-run at a precise point for
  resume testing (signal, startup flag, or role-level halt)

Output: a complete design section in the brainstorm file covering all of the above,
ready to be broken into implementation subtasks.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
