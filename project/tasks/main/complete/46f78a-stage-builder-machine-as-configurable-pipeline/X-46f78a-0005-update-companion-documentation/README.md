# Task: update-companion-documentation

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 46f78a-stage-builder-machine-as-configurable-pipeline             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Update all companion documentation to reflect the new directory structure.
No functional changes — this is purely doc updates after the moves are complete.

## Context

### Files to update

**`ai-builder/orchestrator/README.md`**
- Files table: update `agents/` entry to describe `agents/builder/` subdirectory;
  update `machines/` entry to describe `machines/builder/`
- "Submitting a Pipeline Build Run" example: update `--state-machine` path from
  `machines/default.json` to `machines/builder/default.json`
- "Internal Agents" section: update `"impl"` example path to `agents.builder.tester.TesterAgent`

**`ai-builder/orchestrator/orchestrator.md`**
- Update `ROLES_DIR` description and any references to `roles/` paths
- Update machine JSON example paths

**`ai-builder/orchestrator/agent-roles.md`**
- Update any file path references for role prompt files

**`ai-builder/orchestrator/agents/README.md`**
- Update file table to show `builder/` subdirectory; remove individual agent
  entries (they now live in `agents/builder/README.md`)
- Update `"impl"` example to `agents.builder.tester.TesterAgent`

**`ai-builder/orchestrator/machines/README.md`**
- Update file table to show `builder/` subdirectory

**`CLAUDE.md`**
- Update "Submitting a pipeline build run" example `--state-machine` path
- Update any remaining `roles/` references per subtask 0000/0002 decisions

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
