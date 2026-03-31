# agents/

Pluggable internal agent implementations for the ai-builder orchestrator.

Each class in this package handles one internal pipeline role — a role whose
logic runs in Python rather than spawning an AI subprocess. All classes satisfy
the `InternalAgent` Protocol and can be swapped in a machine JSON file without
touching orchestrator core code.

---

## Files

| File | Description |
|------|-------------|
| `base.py` | `AgentResult` re-export and `InternalAgent` Protocol |
| `context.py` | `AgentContext` dataclass — orchestrator-level constants for agents that need them |
| `loader.py` | `load_internal_agent(impl_path, ctx)` — resolves a dotted class path and instantiates it |
| `builder/` | Builder-specific agent implementations — see [`builder/README.md`](builder/README.md) |

---

## InternalAgent Protocol

```python
@runtime_checkable
class InternalAgent(Protocol):
    def run(self, job_doc: Path, output_dir: Path, **kwargs) -> AgentResult:
        ...
```

Any class with a matching `run` method satisfies this Protocol. The
`@runtime_checkable` decorator enables `isinstance(agent, InternalAgent)` checks
in unit tests. Note: runtime checking verifies method existence only — it does
not check argument types or return type.

---

## AgentContext

Agents that depend on orchestrator-level constants receive an `AgentContext` at
construction time:

```python
@dataclass
class AgentContext:
    run_dir:          Path
    current_job_file: Path
    pm_scripts_dir:   Path
    epic:             str
    output_dir:       Path
    target_repo:      Path | None = None
```

| Field | Used by |
|-------|---------|
| `run_dir` | DecomposeAgent (`set-current-job.sh`), LCHAgent (`--output-dir`) |
| `current_job_file` | LCHAgent (reads current task path) |
| `pm_scripts_dir` | DecomposeAgent, LCHAgent (resolves shell scripts) |
| `epic` | DecomposeAgent, LCHAgent (`--epic` flag) |
| `output_dir` | DecomposeAgent (fallback for `parent_output_dir`) |
| `target_repo` | DecomposeAgent (resolves `in-progress/` path) |

Context-free agents (`TesterAgent`, `DocumenterAgent`) take no constructor arguments.

---

## Configuring via machine JSON

Each internal role in the machine JSON carries an `"impl"` field:

```json
"TESTER": { "agent": "internal", "impl": "agents.builder.tester.TesterAgent", "prompt": null }
```

`load_internal_agent` in `agents/loader.py` resolves this at orchestrator
startup. To use a custom implementation, point `"impl"` at any class whose
`run` method satisfies the `InternalAgent` Protocol.

---

## Unit tests

`tests/unit/test_agents.py` covers:
- `TesterAgent`: pass/fail/missing-command/missing-task-json cases
- `DocumenterAgent`: skip, rebuild, tag routing, no-files cases
- Protocol conformance for all four classes (`assertIsInstance(agent, InternalAgent)`)
- `load_internal_agent` resolution: all `"impl"` paths in `machines/builder/default.json` resolve
  and satisfy the Protocol
