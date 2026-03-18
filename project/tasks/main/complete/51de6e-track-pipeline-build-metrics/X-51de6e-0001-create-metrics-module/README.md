# Task: create-metrics-module

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 51de6e-track-pipeline-build-metrics             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Create `ai-builder/orchestrator/metrics.py` — a pure Python module with no
side effects beyond the functions the orchestrator explicitly calls.

```python
@dataclass
class InvocationRecord:
    role: str
    agent: str        # CLI agent name, e.g. "claude", "gemini"
    n: int            # per-role invocation count
    description: str  # derived from job path (last path segment, strip ID prefix)
    start: datetime
    end: datetime
    elapsed: timedelta
    tokens_in: int
    tokens_out: int
    tokens_cached: int
    outcome: str

def record_invocation(...) -> InvocationRecord
def update_task_doc(build_readme: Path, invocations: list[InvocationRecord]) -> None
def write_run_summary(output_dir: Path, run_data: RunData) -> None
def write_run_metrics_json(output_dir: Path, run_data: RunData) -> None
```

`update_task_doc` rewrites the `## Execution Log` section of the given README,
replacing everything between the header row and the end of the table with the
current invocation rows. The section must already exist (added by template).

`write_run_summary` writes `run-summary.md` with: header block, per-invocation
table, per-role totals, token usage by role with grand total, and a per-agent
invocation count table (agent, count).

`write_run_metrics_json` writes `run-metrics.json` with the same data as a
structured JSON object suitable for cross-run aggregation.

## Context

This module is the seam between the orchestrator and future persistence
(database, dashboard). All metrics logic lives here; orchestrator.py only
calls these functions. Keep it importable and testable in isolation.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
