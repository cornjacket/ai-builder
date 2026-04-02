# Task: refactor-shared-agents

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Move `LCHAgent` and `DecomposeAgent` out of `agents/builder/` into `agents/`
(shared), since both are pipeline-agnostic. Keep `TesterAgent` and
`DocumenterAgent` in `agents/builder/` as they are genuinely builder-specific.

## Context

Both agents are currently in `agents/builder/` but neither has any
builder-specific logic:

- `LCHAgent` — calls `on-task-complete.sh` and maps output tokens to outcomes.
  The `route_on` config extension made it even more general. Any pipeline uses
  the same script and the same mechanism.
- `DecomposeAgent` — calls `new-pipeline-subtask.sh` and writes standard fields
  to `task.json`. The one doc-specific addition (`component_type: integrate`)
  is a universal convention, not builder-specific.

Agents that stay in `agents/builder/`:
- `TesterAgent` — reads `test_command` from `task.json`, a build pipeline concept
- `DocumenterAgent` — scans for ARCHITECT/IMPLEMENTOR documentation, build-specific

**Changes required:**
- Move `agents/builder/lch.py` → `agents/lch.py`
- Move `agents/builder/decompose.py` → `agents/decompose.py`
- Update `impl` paths in `machines/builder/default.json` and `machines/doc/default.json`
- Update imports in `orchestrator.py`
- Update imports in `tests/unit/test_agents.py`
- Update `agents/builder/README.md` and `agents/README.md`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
