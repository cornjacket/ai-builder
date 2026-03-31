# Task: wire-impl-field-into-machine-json-and-orchestrator

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

Add an `"impl"` field to every internal role in `machines/default.json` and
update `orchestrator.py` to resolve agent classes at startup via `importlib`,
replacing the `run_internal_agent` dispatcher with a per-role dispatch table.

## Context

With all four agent classes extracted, the orchestrator needs a way to
discover and instantiate them from configuration rather than hard-coded
`if/elif` branches.

### Changes to `machines/default.json`

Add `"impl"` to each internal role:

```json
"TESTER":                     { "agent": "internal", "impl": "agents.tester.TesterAgent",     "prompt": null },
"DECOMPOSE_HANDLER":          { "agent": "internal", "impl": "agents.decompose.DecomposeAgent", "prompt": null },
"LEAF_COMPLETE_HANDLER":      { "agent": "internal", "impl": "agents.lch.LCHAgent",            "prompt": null },
"DOCUMENTER_POST_ARCHITECT":  { "agent": "internal", "impl": "agents.documenter.DocumenterAgent", "prompt": null },
"DOCUMENTER_POST_IMPLEMENTOR":{ "agent": "internal", "impl": "agents.documenter.DocumenterAgent", "prompt": null }
```

### Changes to `orchestrator.py`

1. **`load_internal_agent(impl_path, ctx)`** — new helper:

```python
def load_internal_agent(impl_path: str, ctx: AgentContext) -> InternalAgent:
    module_path, class_name = impl_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    import inspect
    if "ctx" in inspect.signature(cls.__init__).parameters:
        return cls(ctx=ctx)
    return cls()
```

2. **Startup** — build dispatch table after `ROLES` is loaded:

```python
agent_ctx = AgentContext(
    run_dir=RUN_DIR,
    current_job_file=CURRENT_JOB_FILE,
    pm_scripts_dir=PM_SCRIPTS_DIR,
    epic=EPIC,
    output_dir=OUTPUT_DIR,
    target_repo=TARGET_REPO,
)
internal_agents: dict[str, InternalAgent] = {
    role: load_internal_agent(cfg["impl"], agent_ctx)
    for role, cfg in ROLES.items()
    if cfg.get("agent") == "internal" and "impl" in cfg
}
```

3. **Main loop** — replace the `run_internal_agent(...)` call with:

```python
result = internal_agents[current_role].run(
    job_doc, task_output_dir,
    components=last_components if current_role == "DECOMPOSE_HANDLER" else None,
)
```

4. **Delete** `run_internal_agent`, `_run_decompose_internal`,
   `_run_lch_internal`, `_run_tester_internal`, `_run_documenter_internal`
   from `orchestrator.py` (now live in `agents/`).

5. **Add imports** at the top of `orchestrator.py`:

```python
import importlib
from agents.base import AgentResult, InternalAgent
from agents.context import AgentContext
```

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Unit Tests

Add to `tests/unit/test_agents.py`. These tests verify that the `"impl"` field
in `default.json` resolves to the correct class and that every resolved class
satisfies the Protocol.

```python
class TestLoadInternalAgent(unittest.TestCase):
    def _minimal_ctx(self) -> AgentContext:
        return AgentContext(run_dir=Path("."), current_job_file=Path("."),
                            pm_scripts_dir=Path("."), epic="main",
                            output_dir=Path("."))

    def test_all_impl_paths_resolve(self):
        """Every impl path in default.json must import and instantiate."""
        machine_path = Path("ai-builder/orchestrator/machines/default.json")
        machine = json.loads(machine_path.read_text())
        ctx = self._minimal_ctx()
        for role, cfg in machine["roles"].items():
            if cfg.get("agent") != "internal" or "impl" not in cfg:
                continue
            with self.subTest(role=role):
                agent = load_internal_agent(cfg["impl"], ctx)
                self.assertIsNotNone(agent)

    def test_all_resolved_agents_satisfy_protocol(self):
        """Every resolved agent must pass the isinstance Protocol check."""
        machine_path = Path("ai-builder/orchestrator/machines/default.json")
        machine = json.loads(machine_path.read_text())
        ctx = self._minimal_ctx()
        for role, cfg in machine["roles"].items():
            if cfg.get("agent") != "internal" or "impl" not in cfg:
                continue
            with self.subTest(role=role):
                agent = load_internal_agent(cfg["impl"], ctx)
                self.assertIsInstance(agent, InternalAgent)
```
