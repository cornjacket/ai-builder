# Task: implement-replay-mode

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

Add `--replay-from <recording-dir>` flag to orchestrator.py. When set:
- At startup, load `recording.json` and check for prompt drift (recompute prompt hashes, abort with a diff if any changed; `--ignore-prompt-drift` to override)
- In `run_agent()`, when the current role is an AI role, restore the workspace to the next recording commit instead of calling the AI, then return the pre-recorded response
- All non-AI handlers (DECOMPOSE_HANDLER, LCH) re-run normally against the restored state
- Replay honours `--halt-after-ai-invocation N` so partial replay is possible

## Context

See brainstorm `sandbox/brainstorms/brainstorm-pipeline-stop-and-replay.md`, sections "Replay: Flag on Orchestrator vs Separate Script" and "Prompt Drift Detection". Depends on 0001 (record mode) — a recording must exist before replay can be used.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
