# Task: move-machine-configs-to-machines-builder

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

Move all four machine JSON files from `machines/` into `machines/builder/`
and update their `"prompt"` path strings to reflect the new role file locations.

## Context

### Files to move

| From | To |
|------|----|
| `machines/default.json` | `machines/builder/default.json` |
| `machines/simple.json` | `machines/builder/simple.json` |
| `machines/default-gemini.json` | `machines/builder/default-gemini.json` |
| `machines/simple-gemini.json` | `machines/builder/simple-gemini.json` |

### Prompt path updates inside the JSON files

All `"prompt"` values are relative to `REPO_ROOT`. After `roles/` moves to
`ai-builder/roles/builder/`, the paths must be updated:

| Old | New |
|-----|-----|
| `"roles/ARCHITECT.md"` | `"ai-builder/roles/builder/ARCHITECT.md"` |
| `"roles/IMPLEMENTOR.md"` | `"ai-builder/roles/builder/IMPLEMENTOR.md"` |
| `"roles/TESTER.md"` | `"ai-builder/roles/builder/TESTER.md"` |

### New files

- `machines/builder/README.md` — describes the builder machine variants and
  when to use each

### `machines/README.md` update

Update the file index to list `builder/` instead of the individual JSON files.

### Ripple: any documentation or scripts referencing specific machine paths

Search for hardcoded references to `machines/default.json`,
`machines/simple.json`, etc. outside of tests and update them. In particular:
- `orchestrator/README.md` — the "Submitting a Pipeline Build Run" example
  uses `ai-builder/orchestrator/machines/default.json`
- `CLAUDE.md` — same example in "Submitting a pipeline build run" section
- Any regression test `reset.sh` or config that passes `--state-machine`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
