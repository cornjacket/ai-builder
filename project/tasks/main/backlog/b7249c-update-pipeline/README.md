# Task: update-pipeline

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | pipeline, refactor               |
| Priority    | MED           |
| Next-subtask-id | 0000               |

## Goal

Implement a large-codebase update pipeline that applies a systematic change
(API migration, convention enforcement, dependency upgrade, etc.) across an
existing source tree. UPDATE_IMPLEMENTOR reads and partially rewrites existing
files rather than generating them from scratch. Output: modified source files
in place + per-level update summary docs as a permanent audit trail.

## Context

Brainstorm: `sandbox/brainstorm-pipeline-repurposing.md`

Uses the same orchestrator infrastructure as the build pipeline. New elements:

- `update.json` machine file
- Role prompts: UPDATE_ARCHITECT (decompose + atomic), UPDATE_IMPLEMENTOR, UPDATE_INTEGRATOR
- POST_IMPLEMENT_HANDLER configured with `go build ./... && go test ./...`
- `"type": "file"` component support (see 49352f-0003/0004)
- Level-scoped handoff history (see 49352f-0005) so UPDATE_INTEGRATOR can verify
  cross-component consistency before advancing

**Role mapping:**

| Role | Job |
|------|-----|
| UPDATE_ARCHITECT (decompose) | Identify sub-components and files to update; design the update strategy for this level |
| UPDATE_IMPLEMENTOR | Apply changes to each file — judgment calls on how to apply the convention/migration; reads existing file before modifying |
| POST_IMPLEMENT_HANDLER | `go build ./... && go test ./...` — verify changes compile and pass |
| UPDATE_INTEGRATOR | Verify cross-component consistency; check no files were missed; produce level update summary |

**Key difference from build pipeline:** source files already exist and contain
logic that must be preserved. UPDATE_IMPLEMENTOR does partial rewrites, not fresh
writes. The ARCHITECT's update strategy must be specific enough to preserve
existing logic while applying the change.

Update summaries are permanent (not scratch) — they serve as an audit trail of
what was changed and why at each level.

**Depends on:** 49352f subtasks 0003, 0004, 0005.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
