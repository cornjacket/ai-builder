# Task: tester-must-not-call-task-scripts

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 3fa24b-bug-handler-prompt-inefficiency             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Ensure pipeline agents — specifically TESTER — never call task management scripts
(`complete-task.sh`, `move-task.sh`, etc.). Task lifecycle is owned exclusively by
the LEAF_COMPLETE_HANDLER via `on-task-complete.sh`.

## Context

During the platform-monolith regression run (2026-03-18), the TESTER called
`complete-task.sh --parent` after tests passed, renaming the task directory to
`X-68699c-0000-metrics`. When LEAF_COMPLETE_HANDLER subsequently called
`on-task-complete.sh` with the original path, the directory no longer existed and
the script failed with "File not found", halting the pipeline.

**Root cause:** The agent subprocess runs with `cwd=output_dir` (see
`agent_wrapper.py` line 48). Claude Code walks up from cwd to find CLAUDE.md files.
The output dir sits inside the ai-builder repo root, so the agent loads
`ai-builder/CLAUDE.md` — our own developer instructions — which contains the rule:
"When a subtask is finished, always run `complete-task.sh --parent`". The TESTER
read this rule and followed it.

**Fixes applied:**
1. `roles/TESTER.md` — added explicit prohibition: "Do NOT call complete-task.sh
   or move any task directories. Task completion is handled by LEAF_COMPLETE_HANDLER."
2. `target/project/tasks/scripts/on-task-complete.sh` — added defense-in-depth:
   if the task directory is already X-prefixed, skip the complete-task.sh step
   and proceed directly to advance-pipeline.sh.

**Deeper issue to track separately:** The cwd=output_dir choice means all pipeline
agents inherit our developer CLAUDE.md. Rules written for humans and AI developers
working on ai-builder itself bleed into the pipeline. This needs a proper solution —
either run agents with a neutral cwd, or add a pipeline-context marker that
overrides developer rules. See follow-on task.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
