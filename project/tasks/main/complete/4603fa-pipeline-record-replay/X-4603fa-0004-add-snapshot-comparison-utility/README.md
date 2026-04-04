# Task: add-snapshot-comparison-utility

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 4603fa-pipeline-record-replay             |
| Priority    | —           |
| Created     | 2026-04-02            |
| Completed | 2026-04-02 |
| Next-subtask-id | 0000               |

## Goal

Add a utility (script or Python module) that diffs a recording commit against the current working tree. Given a recording dir and an invocation number N, it resolves the commit SHA from `recording.json`, runs `git diff <sha>` inside the recording repo, and prints the result. An empty diff means the working tree matches the recording at that point exactly.

Used for: replay verification (diff should be empty after replay to N), gold comparison (diff a known-good recording against a fresh run), and inspecting handler side effects (diff inv-N vs inv-N+1).

## Context

See brainstorm `sandbox/brainstorms/brainstorm-pipeline-stop-and-replay.md`, section "Comparing a Recording Snapshot to the Output Directory". Depends on 0001 (record mode).

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
