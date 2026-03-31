# Task: move-agent-impls-into-agents-builder

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

Move the four builder-specific agent implementations from `agents/` into a
new `agents/builder/` subdirectory. Update `"impl"` paths in all machine JSON
files and verify unit tests still pass.

## Context

### Files to move

| From | To |
|------|----|
| `agents/tester.py` | `agents/builder/tester.py` |
| `agents/tester.md` | `agents/builder/tester.md` |
| `agents/documenter.py` | `agents/builder/documenter.py` |
| `agents/documenter.md` | `agents/builder/documenter.md` |
| `agents/decompose.py` | `agents/builder/decompose.py` |
| `agents/decompose.md` | `agents/builder/decompose.md` |
| `agents/lch.py` | `agents/builder/lch.py` |
| `agents/lch.md` | `agents/builder/lch.md` |

### New files

- `agents/builder/__init__.py` — empty, marks as package
- `agents/builder/README.md` — overview of builder-specific agents

### Changes to machine JSON files

All four machine configs contain `"impl"` fields that must be updated:

| Old | New |
|-----|-----|
| `"agents.tester.TesterAgent"` | `"agents.builder.tester.TesterAgent"` |
| `"agents.decompose.DecomposeAgent"` | `"agents.builder.decompose.DecomposeAgent"` |
| `"agents.lch.LCHAgent"` | `"agents.builder.lch.LCHAgent"` |
| `"agents.documenter.DocumenterAgent"` | `"agents.builder.documenter.DocumenterAgent"` |

Update in-place in the current locations (`machines/*.json`) — the machine
configs themselves are moved in subtask 0003.

### Changes to `agents/README.md`

Update the file table to reflect moved files and link to `agents/builder/README.md`.

### Verification

Run `python3 -m unittest discover -s tests/unit` — all 60 tests must pass.
The `TestLoadInternalAgent` tests in `test_agents.py` exercise the `"impl"`
resolution path end-to-end, so they will catch any incorrect dotted path.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
