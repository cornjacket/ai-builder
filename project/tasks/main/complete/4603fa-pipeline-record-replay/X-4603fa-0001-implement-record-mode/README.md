# Task: implement-record-mode

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

Add `--record-to <dir>` flag to orchestrator.py. When set:
- Initialize a git repo in the regression workspace if one does not exist
- After every invocation (AI roles and non-AI handlers), commit the full workspace with message `inv-N ROLE outcome`
- At run end, write `recording.json` manifest to the recording dir: recorded_at timestamp, ai_builder_commit SHA, prompt_hashes for all role `.md` files used, and an ordered invocations list with `{n, role, outcome, commit_sha, ai}` per entry

The `ai` flag distinguishes AI roles (ARCHITECT, IMPLEMENTOR, TESTER) from handlers (DECOMPOSE_HANDLER, LCH). The manifest's invocation list is derived from the execution_log already written to the top-level task.json, cross-referenced with commit SHAs captured during the run.

## Context

See brainstorm `sandbox/brainstorms/brainstorm-pipeline-stop-and-replay.md`, sections "Recording Manifest and Execution Log" and "Prompt Drift Detection".

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
