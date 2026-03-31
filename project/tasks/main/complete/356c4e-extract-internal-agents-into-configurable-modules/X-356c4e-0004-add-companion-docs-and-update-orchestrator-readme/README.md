# Task: add-companion-docs-and-update-orchestrator-readme

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 356c4e-extract-internal-agents-into-configurable-modules             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Write companion `.md` files for each new source file in `agents/`, add a
`README.md` for the `agents/` package itself, and update
`ai-builder/orchestrator/README.md` to document the new package structure and
the `"impl"` configuration field.

## Context

Per project documentation guidelines every new source file needs a companion
`.md` and every directory needs a `README.md`.

### Files to create

**`agents/README.md`** — package overview:
- Purpose: typed, pluggable internal agent implementations
- Lists all modules: `base.py`, `context.py`, `tester.py`, `documenter.py`,
  `decompose.py`, `lch.py`
- Explains `InternalAgent` Protocol and `AgentContext` injection pattern
- Shows how `"impl"` in machine JSON maps to a class path resolved at startup

**`agents/base.md`** — documents `AgentResult` fields and `InternalAgent` Protocol

**`agents/context.md`** — documents each `AgentContext` field and which agents use it

**`agents/tester.md`** — inputs, outputs, and side effects of `TesterAgent.run`

**`agents/documenter.md`** — inputs, outputs, and side effects of `DocumenterAgent.run`

**`agents/decompose.md`** — inputs, outputs, and side effects of `DecomposeAgent.run`; documents the `components` kwarg

**`agents/lch.md`** — inputs, outputs, and side effects of `LCHAgent.run`; documents `TOP_RENAME_PENDING` protocol

### Updates to `orchestrator/README.md`

- Add a "Package layout" section listing `agents/` alongside existing files
- Update "Internal agents" section to explain the `"impl"` field and
  `load_internal_agent` resolution
- Remove any reference to the deleted private functions

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
