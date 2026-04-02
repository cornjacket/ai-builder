---
Purpose: Render a README.md for a pipeline task from its task.json.
Tags: orchestrator, documentation, pipeline
---

# render_readme.py

Generates a human-readable `README.md` alongside a pipeline `task.json`.
`task.json` is authoritative; `README.md` is a derived view — never written
directly by pipeline agents.

## Inputs

| Parameter | Type | Description |
|-----------|------|-------------|
| `task_json_path` | `Path` | Path to the `task.json` to render |

## Outputs

Writes `README.md` in the same directory as `task.json`. Overwrites any
existing README.

## Render modes

### TOP-level task (`level == "TOP"`)

| Section | Source in task.json |
|---------|---------------------|
| Title | `parent` field (or `name` / first line of `goal` as fallback) |
| Run Summary | `run_summary` (written at pipeline completion) |
| Execution Log | `execution_log` (updated after each invocation) |
| Subtask list | `subtasks` array |

### Non-TOP pipeline subtask

| Section | Source in task.json | When present |
|---------|---------------------|--------------|
| Title | `name` (or first line of `goal`) | always |
| Goal | `goal` | always (set by decompose.py) |
| Context | `context` | always (breadcrumb trail set by decompose.py) |
| Design | `design` | after ARCHITECT design-ready outcome |
| Acceptance Criteria | `acceptance_criteria` | after ARCHITECT design-ready outcome |
| Test Command | `test_command` | after ARCHITECT design-ready outcome |
| Subtask list | `subtasks` | composite nodes only |

## CLI usage

```bash
python3 render_readme.py --task path/to/task.json
```

## In-process usage

```python
from render_readme import render_task_readme
render_task_readme(Path("path/to/task.json"))
```

## Orchestrator integration

Called by `orchestrator.py` in two places:

1. **After each invocation** — re-renders the TOP-level task README (and the
   active task README if different) to show live progress.
2. **At pipeline completion** — final render after `write_metrics_to_task_json`
   writes the complete `run_summary`.
