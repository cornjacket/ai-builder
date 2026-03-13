# ai-builder

The ai-builder system drives AI agents through a structured pipeline to
architect, implement, and test software from a job specification.

---

## File Index

| Path | Description |
|------|-------------|
| `orchestrator/` | Pipeline engine: CLI, routing, prompt construction, agent dispatch |
| `oracle/` | *(planned)* N-phase model, phase types, Oracle role definition |

---

## Overview

The pipeline is a loop over roles. Each role receives a job document and
produces an `OUTCOME` that determines the next role. The orchestrator drives
the loop; agents do the work.

```
  [job doc]
      │
      ▼
  ARCHITECT ──DONE──► IMPLEMENTOR ──DONE──► TESTER ──DONE──► (halt or TASK_MANAGER)
      ▲                    │                   │
      └──NEEDS_ARCHITECT───┘                   └──FAILED──► IMPLEMENTOR
```

Two modes:

- **Non-TM mode** (`--job`): single job document, pipeline halts when TESTER passes.
- **TM mode** (`--target-repo`): TASK_MANAGER decomposes a project into tasks and
  drives the pipeline task-by-task until the backlog is empty.

See [`orchestrator/README.md`](orchestrator/README.md) for the full pipeline
reference including routing tables, data flow, and output directory layout.

---

## References

- [`orchestrator/README.md`](orchestrator/README.md) — pipeline internals
- [`../roles/`](../roles/) — role definitions (ARCHITECT, IMPLEMENTOR, TESTER, TASK_MANAGER, DOCUMENTER)
- [`../tests/regression/`](../tests/regression/) — regression test suite
