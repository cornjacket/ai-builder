# Unit Tests

Python unit tests for the ai-builder orchestrator modules.

## Run

From the repo root:

```bash
python3 -m unittest discover -s tests/unit -v
```

## Files

| File | Covers |
|------|--------|
| `test_metrics.py` | `metrics.py` — `_fmt_elapsed`, `description_from_job_path`, `record_invocation`, `update_task_doc`, `write_run_summary`, `write_run_metrics_json`, `write_summary_to_readme`, `_build_summary_lines` |
| `test_orchestrator_validation.py` | TM-mode validation regex patterns from `orchestrator.py` — Task-type and Level field matching |

No external dependencies. Uses only Python standard library (`unittest`, `pathlib`, `json`, `tempfile`).
