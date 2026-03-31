# Task: define-internalagent-protocol-and-agentcontext

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

Create `ai-builder/orchestrator/agents/` package with two foundation files:
`base.py` defining the `InternalAgent` Protocol and `AgentResult` type, and
`context.py` defining the `AgentContext` dataclass that carries orchestrator-level
constants needed by agents that shell out to task management scripts.

## Context

Before any agent can be extracted, the shared interface and dependency
injection container must exist. All subsequent subtasks depend on these.

Files to create:

**`agents/__init__.py`** — empty, marks the directory as a package.

**`agents/base.py`**
```python
from typing import Protocol, runtime_checkable
from pathlib import Path
from dataclasses import dataclass

@dataclass
class AgentResult:
    exit_code: int   # 0=ok, 1=error, 2=timeout
    response: str
    tokens_in: int = 0
    tokens_out: int = 0
    tokens_cached: int = 0

@runtime_checkable
class InternalAgent(Protocol):
    def run(self, job_doc: Path, output_dir: Path, **kwargs) -> AgentResult:
        ...
```

`@runtime_checkable` enables `isinstance(agent, InternalAgent)` checks in unit
tests. Note: it only verifies method existence, not full signature conformance —
that is a limitation of Python's runtime Protocol support.

**`agents/context.py`**
```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class AgentContext:
    """Orchestrator-level constants injected into agents that need them."""
    run_dir:        Path
    current_job_file: Path
    pm_scripts_dir: Path
    epic:           str
    output_dir:     Path
    target_repo:    Path | None = None
```

Note: `AgentResult` currently lives in `orchestrator.py`. This subtask moves
the definition to `agents/base.py` and updates the import in `orchestrator.py`.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
