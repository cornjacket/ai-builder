# Task: add-gemini-machine-files

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | e62647-add-test-support-for-gemini-subagents             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Promote the `.gemini` scratch machine files to proper committed files in
`ai-builder/orchestrator/machines/`.

## Context

Two scratch files exist as untracked `.gemini` variants:
- `machines/default.json.gemini` — TM machine (all roles set to `"agent":"gemini"`)
- `machines/simple.json.gemini`  — simple machine (all roles set to `"agent":"gemini"`)

Steps:
1. Copy to `machines/default-gemini.json` and `machines/simple-gemini.json`
2. Delete the `.gemini` scratch files
3. Add entries to `machines/README.md` (if it exists)

No changes to the JSON content — they are structurally correct already.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
