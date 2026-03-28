# Unit Tests

Python unit tests for the ai-builder orchestrator modules. These are fast,
dependency-free tests that run against the Python source directly — no pipeline
execution, no AI agents, no external services.

## Run

From the repo root:

```bash
python3 -m unittest discover -s tests/unit -v
```

All tests use only the Python standard library (`unittest`, `pathlib`, `json`,
`tempfile`, `datetime`). No external packages required.

## Files

| File | Covers |
|------|--------|
| `test_metrics.py` | `metrics.py` — elapsed formatting, job path description, invocation recording, execution log table, `write_metrics_to_task_json` (execution_log + run_summary to task.json), `write_summary_to_readme`, `_build_summary_lines` |
| `test_orchestrator_validation.py` | TM-mode entry point validation from `orchestrator.py` — task.json task-type and level field checking, resume bypass |

## What is tested

**`test_metrics.py`** covers the metrics module's full public surface:
- `_fmt_elapsed` — elapsed time formatting (sub-minute, mixed, large values)
- `description_from_job_path` — human-readable task name extraction from path
- `record_invocation` — appending invocation records to a RunData object
- `_build_summary_lines` — Markdown summary table generation (invocations, per-role totals, token usage by role, per-agent counts)
- `update_task_doc` — writing/updating the `## Execution Log` table in a task README
- `write_metrics_to_task_json` — writing `execution_log` to task.json after each invocation; writing `run_summary` totals when `final=True`
- `write_summary_to_readme` — appending a `## Run Summary` section to the Level:TOP README

**`test_orchestrator_validation.py`** covers the TM-mode entry point guard:
- Rejects USER-TASK and USER-SUBTASK task types
- Rejects `Level: INTERNAL` and `Level: —` without `--resume`
- Accepts `Level: INTERNAL` with `--resume` (resume skips the Level:TOP check)
- Rejects missing or malformed task.json
- Accepts a well-formed PIPELINE-SUBTASK with `Level: TOP`
