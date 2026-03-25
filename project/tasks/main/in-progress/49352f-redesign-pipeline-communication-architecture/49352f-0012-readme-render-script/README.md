# Task: readme-render-script

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 49352f-redesign-pipeline-communication-architecture             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Write a `render-readme.py` script that generates a `README.md` for a pipeline
task from its `task.json`. Integrate it into the orchestrator so it runs after
each pipeline stage (live monitoring) and again on `HANDLER_ALL_DONE` (final
render).

## Context

Under the JSON-native model, `task.json` is authoritative. README.md for
pipeline tasks is a generated view — never written directly. This script
provides the rendering layer.

**Two render calls per pipeline run:**
1. **After each stage** — re-render the TOP-level task README and the currently
   active task README to show live progress (execution log, subtask completion).
2. **On `HANDLER_ALL_DONE`** — final render of both with complete metrics and
   execution log from `task.json`.

**TOP-level task README template:**
```markdown
# <task-name>

## Run Summary
| Field | Value |
|-------|-------|
| Start | ... |
| End | ... |
| Total tokens in | ... |
| ...  |

## Execution Log
| Role | Agent | Outcome | Tokens In | Tokens Out | Timestamp |
|------|-------|---------|-----------|------------|-----------|
| ARCHITECT | gemini | ARCHITECT_DECOMPOSITION_READY | 21000 | 1800 | ... |

## Subtasks
- [x] store
- [x] handlers
- [x] integrate
```

**Active task README template:**
Subtask completion list only. Execution log lives at the TOP level.

**Usage:**
```bash
python3 render-readme.py --task path/to/task.json
```

The script is also callable by the orchestrator in-process via an importable
function.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
