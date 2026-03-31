# Task: extract-internal-agents-into-configurable-modules

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Next-subtask-id | 0005 |

## Goal

Extract all four internal agent implementations from `orchestrator.py` into
a dedicated `agents/` package. Wire each agent class into `machines/default.json`
via an `"impl"` field so that custom pipeline machine definitions can swap
implementations without touching orchestrator core code. Apply the Python
`Protocol` pattern to define a stable `InternalAgent` interface.

## Context

All internal agent logic lives inline in `orchestrator.py` as private
functions (`_run_tester_internal`, `_run_documenter_internal`,
`_run_decompose_internal`, `_run_lch_internal`). As new pipelines are
defined — with different test runners, documenter strategies, or decompose
behaviours — this logic will accumulate inside a 1,500-line file with no
clean boundary.

Extracting into a typed `agents/` package with a `Protocol`-based interface
establishes the seam early. The machine JSON already names roles; adding an
`"impl"` key makes internal agents as configurable as AI agent prompts are
today.

### Python Protocols vs Go/Java interfaces

Python uses structural typing via `typing.Protocol`. Any class with a
matching method signature satisfies the protocol without explicit declaration
— identical to Go's implicit interface satisfaction. Static checking is
enforced by mypy. Example:

```python
# agents/base.py
from typing import Protocol
from pathlib import Path

class InternalAgent(Protocol):
    def run(self, job_doc: Path, output_dir: Path, **kwargs) -> AgentResult:
        ...
```

### Machine JSON wiring

```json
"TESTER": {
  "agent": "internal",
  "impl":  "agents.tester.TesterAgent"
}
```

Orchestrator resolves at startup:

```python
import importlib

def load_internal_agent(impl_path: str) -> InternalAgent:
    module_path, class_name = impl_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)()

internal_agents = {
    role: load_internal_agent(cfg["impl"])
    for role, cfg in ROLES.items()
    if cfg.get("agent") == "internal" and "impl" in cfg
}
```

Main loop replaces the `run_internal_agent` dispatcher with:

```python
result = internal_agents[current_role].run(job_doc, task_output_dir, **extras)
```

### Dependency coupling (from investigation)

| Agent | Orchestrator globals needed | Complexity |
|---|---|---|
| `TesterAgent` | None | Low |
| `DocumenterAgent` | None | Low |
| `DecomposeAgent` | OUTPUT_DIR, TARGET_REPO, EPIC, PM_SCRIPTS_DIR, RUN_DIR | Medium |
| `LCHAgent` | CURRENT_JOB_FILE, PM_SCRIPTS_DIR, EPIC, RUN_DIR | Medium |

`DecomposeAgent` and `LCHAgent` require an injected config object for
their orchestrator-level constants. An `AgentContext` dataclass passed
at construction time is the clean solution.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-356c4e-0000-define-internalagent-protocol-and-agentcontext](X-356c4e-0000-define-internalagent-protocol-and-agentcontext/)
- [x] [X-356c4e-0001-extract-tester-and-documenter-agents](X-356c4e-0001-extract-tester-and-documenter-agents/)
- [x] [X-356c4e-0002-extract-decompose-and-lch-agents](X-356c4e-0002-extract-decompose-and-lch-agents/)
- [x] [X-356c4e-0003-wire-impl-field-into-machine-json-and-orchestrator](X-356c4e-0003-wire-impl-field-into-machine-json-and-orchestrator/)
- [x] [X-356c4e-0004-add-companion-docs-and-update-orchestrator-readme](X-356c4e-0004-add-companion-docs-and-update-orchestrator-readme/)
<!-- subtask-list-end -->

## Notes

_None._
