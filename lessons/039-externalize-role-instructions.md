# 039 — Externalize Role Instructions from Code

**Context:** AIDT+ orchestrator experiments.

**Observed:** Role instructions for ARCHITECT, IMPLEMENTOR, and TESTER live
inside `orchestrator.py` as Python string literals. Every time an agent
misbehaves (e.g. lesson 038), the code file must be edited. Instructions are
hard to read in isolation and change for different reasons than the orchestration
logic.

**Proposed fix:** Extract role instructions into separate markdown files
(`ARCHITECT.md`, `IMPLEMENTOR.md`, `TESTER.md`) under a `roles/` directory.
Separately, extract orchestration config (agent assignment, timeouts, routing)
into `roles/pipeline.yaml`. The orchestrator reads both at startup.

**Benefits:**
- Instructions are readable and editable without touching code
- Role definitions and pipeline wiring change independently and for different reasons
- Natural place to accumulate rules as new agent behaviors are discovered
- Role `.md` files could be passed directly to agents as readable context

**Two distinct audiences within pipeline config:**

| Field | Audience | Changes when |
|---|---|---|
| `agent`, `timeout`, `routes` | Orchestrator | Pipeline redesign, model swap, perf tuning |
| `*.md` instructions | Agent | Observed misbehavior, scope refinement |

**Status:** Not yet implemented. Tracked for the next orchestrator iteration.
