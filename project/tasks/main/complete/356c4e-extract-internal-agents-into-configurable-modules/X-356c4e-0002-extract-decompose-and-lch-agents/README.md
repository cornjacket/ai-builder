# Task: extract-decompose-and-lch-agents

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

Move `_run_decompose_internal` into `agents/decompose.py` as `DecomposeAgent`
and `_run_lch_internal` into `agents/lch.py` as `LCHAgent`. Both require
orchestrator-level constants injected via `AgentContext`; no globals may be
referenced directly.

## Context

Unlike the Tester and Documenter, these two agents reference module-level
globals and must receive them through the `AgentContext` dataclass defined in
subtask 0000.

**`agents/decompose.py`** — wraps `_run_decompose_internal` (~120 lines):
- Receives `job_doc` and `components` list (from ARCHITECT JSON) as call-site
  kwargs alongside `AgentContext`
- Uses `ctx.output_dir`, `ctx.target_repo`, `ctx.epic`, `ctx.pm_scripts_dir`
  to call `new-pipeline-subtask.sh` and populate child `task.json` entries
- Returns `AgentResult` with `HANDLER_SUBTASKS_READY` or error

**`agents/lch.py`** — wraps `_run_lch_internal` (~55 lines):
- Uses `ctx.current_job_file` (reads current task path) and
  `ctx.pm_scripts_dir` (resolves `on-task-complete.sh`)
- Uses `ctx.run_dir` as `--output-dir` for `set-current-job.sh`
- Uses `ctx.epic` for the `--epic` flag
- Parses `NEXT`/`DONE`/`STOP_AFTER` and `TOP_RENAME_PENDING` tokens from
  `on-task-complete.sh` stdout
- Returns `AgentResult` with `HANDLER_SUBTASKS_READY`, `HANDLER_ALL_DONE`, or
  `HANDLER_STOP_AFTER`

Constructor signature for both classes:

```python
def __init__(self, ctx: AgentContext) -> None:
    self.ctx = ctx
```

`run` signature (satisfies `InternalAgent` Protocol):

```python
def run(self, job_doc: Path, output_dir: Path, **kwargs) -> AgentResult:
```

`DecomposeAgent.run` reads `components` from `kwargs["components"]`.

After extraction, the private functions in `orchestrator.py` are deleted and
replaced with imports.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Unit Tests

Add to `tests/unit/test_agents.py`.

**DecomposeAgent**

DecomposeAgent calls `new-pipeline-subtask.sh` and reads/writes `task.json`
files — it requires a real (temp) task tree. Use the same fixture pattern as
the component tests: copy a minimal `in-progress/` tree into a temp dir.

```python
class TestDecomposeAgent(unittest.TestCase):
    def _make_ctx(self, tmp: Path) -> AgentContext:
        # Minimal fixture: create an in-progress task tree + output dir
        # Point pm_scripts_dir at the real scripts directory
        ...

    def test_creates_component_subtasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = self._make_ctx(Path(tmp))
            agent = DecomposeAgent(ctx=ctx)
            components = [
                {"name": "store", "complexity": "medium", "description": "data layer"},
            ]
            result = agent.run(job_doc=..., output_dir=..., components=components)
            self.assertEqual(result.exit_code, 0)
            self.assertIn("HANDLER_SUBTASKS_READY", result.response)
            # Assert subtask directory was created in the task tree

    def test_satisfies_internal_agent_protocol(self):
        # Construct with a minimal ctx; Protocol check doesn't require a real ctx
        ctx = AgentContext(run_dir=Path("."), current_job_file=Path("."),
                           pm_scripts_dir=Path("."), epic="main",
                           output_dir=Path("."))
        self.assertIsInstance(DecomposeAgent(ctx=ctx), InternalAgent)
```

**LCHAgent**

LCHAgent calls `on-task-complete.sh`, which in turn calls `advance-pipeline.sh`
and friends. A real subprocess test requires a live task tree. For the Protocol
check, instantiation alone is sufficient.

```python
class TestLCHAgent(unittest.TestCase):
    def test_satisfies_internal_agent_protocol(self):
        ctx = AgentContext(run_dir=Path("."), current_job_file=Path("."),
                           pm_scripts_dir=Path("."), epic="main",
                           output_dir=Path("."))
        self.assertIsInstance(LCHAgent(ctx=ctx), InternalAgent)
```

Full behavioural coverage for LCHAgent is provided by the existing component
tests (steps 02–04), which exercise `on-task-complete.sh` end-to-end. A
standalone unit test is not practical without a complete sandbox fixture.
