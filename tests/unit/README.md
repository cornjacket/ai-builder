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

---

## test_orchestrator_validation.py — Entry point guard (12 tests)

Tests the orchestrator's TM-mode entry point validation. The logic reads
`task.json`, checks `task-type == PIPELINE-SUBTASK` and `level == TOP`, and
accepts `--resume` as a bypass for the level check.

**How it works:** Writes a real `task.json` to a temp directory, calls the
replicated validation function, checks the boolean result and error message.

Note: the validation logic is replicated locally in the test file rather than
imported from `orchestrator.py`, which has argparse side effects at import time.

| Class | What it tests |
|-------|--------------|
| `TestTaskTypeValidation` | Accepts PIPELINE-SUBTASK; rejects USER-TASK, USER-SUBTASK; rejects missing file |
| `TestLevelValidation` | Accepts TOP; rejects INTERNAL and `—`; accepts INTERNAL when `resume=True` |
| `TestCombinedValidation` | Happy path, type check failure, level check failure, malformed JSON |

---

## test_metrics.py — Metrics module (34 tests)

Tests `metrics.py` via direct import. Six categories:

| Class | Tests | What it tests | How |
|-------|-------|--------------|-----|
| `TestFmtElapsed` | 5 | `_fmt_elapsed` — formats a timedelta as `"47s"` or `"2m 05s"` | Passes timedeltas, asserts formatted string |
| `TestDescriptionFromJobPath` | 6 | `description_from_job_path` — strips hex prefix and NNNN from a task path to get a human name | Passes Path objects, asserts extracted name |
| `TestRecordInvocation` | 2 | `record_invocation` — appends an InvocationRecord to RunData, computes elapsed | Builds a RunData, calls function, checks list length and field values |
| `TestBuildSummaryLines` | 9 | `_build_summary_lines` — generates the full Markdown summary (header table, invocations, per-role totals, token usage, per-agent counts) | Builds a run with known invocations, joins lines to text, asserts section headers and values present |
| `TestUpdateTaskDoc` | 5 | `update_task_doc` — writes/rewrites the `## Execution Log` table in a task README | Writes a README with/without the section to a temp file, calls function, reads back and asserts content |
| `TestWriteMetricsToTaskJson` | 5 | `write_metrics_to_task_json` — writes `execution_log` to task.json each invocation; writes `run_summary` totals when `final=True` | Writes a minimal task.json, calls function, parses JSON back and asserts fields |
| `TestWriteSummaryToReadme` | 2 | `write_summary_to_readme` — appends `## Run Summary` section to a README | Writes a README to temp file, calls function, reads back and checks sections |
