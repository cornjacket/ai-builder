# Task: write-replay-regression-test

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 4603fa-pipeline-record-replay             |
| Priority    | —           |
| Created     | 2026-04-02            |
| Completed | 2026-04-03 |
| Next-subtask-id | 0000               |

## Goal

Add a replay-based regression test for the user-service pipeline. The test:
1. Runs reset.sh to initialise a clean workspace in `sandbox/regressions/user-service/`
2. Runs the orchestrator with `--record-to` to capture a reference recording
3. Runs reset.sh again to wipe the workspace back to initial state
4. Replays the recording with `--replay-from` and verifies the output matches the recording using the snapshot comparison utility (empty diff at each invocation checkpoint)

This test exercises the full orchestrator mechanic loop at zero token cost and deterministically. A diff failure means orchestrator behaviour changed, not the AI.

## Context

Depends on 0001 (record mode), 0003 (replay mode), and 0004 (snapshot comparison utility).

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
