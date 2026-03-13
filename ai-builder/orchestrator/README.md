# ai-builder pipeline

The orchestrator core. Drives a multi-role AI pipeline that takes a job
document from input to tested implementation through specialist agents.

---

## Files

| File | Description |
|------|-------------|
| `orchestrator.py` | Main pipeline loop: routes between roles, manages state, parses outcomes |
| `agent_wrapper.py` | Spawns agent CLI subprocesses, streams output, returns results |
| `JOB-TEMPLATE.md` | Job template for direct (non-decomposition) pipeline runs |
| `JOB-service-build.md` | Job template for ARCHITECT decompose mode — produces component table |
| `JOB-component-design.md` | Job template for ARCHITECT design mode — produces Design + Acceptance Criteria |
| `orchestrator.md` | Code companion: inputs, outputs, internals for orchestrator.py |
| `agent_wrapper.md` | Code companion: inputs, outputs, internals for agent_wrapper.py |
| `job-format.md` | Job document format and agent output field specification |
| `routing.md` | ROUTES table, outcome values per role, DOCUMENTER hook |
| `decomposition.md` | Multi-level decomposition protocol, task tree navigation |
| `open-questions.md` | Unresolved design questions |

---

## Pipeline Overview

The pipeline runs specialist AI agents in sequence. Each agent reads a shared
job document, does its work, and emits a structured outcome. The orchestrator
routes between agents based on that outcome.

**Two modes:**

- **Non-TM mode** (`--job`): single job document, pipeline runs once.
  Starts at ARCHITECT, terminates when TESTER passes.

- **TM mode** (`--target-repo`): Oracle-driven outer loop. The Oracle
  prepares a job document and invokes the orchestrator. The pipeline always
  starts at ARCHITECT. TASK_MANAGER runs only at the end to update the task
  system. The Oracle reads the result and decides whether to start another
  pipeline run.

**Roles and agents:**

| Role | Agent | Responsibility |
|------|-------|----------------|
| ARCHITECT | claude | Designs the solution; fills Design + Acceptance Criteria |
| IMPLEMENTOR | gemini | Implements exactly what ARCHITECT designed |
| TESTER | claude | Verifies implementation against Acceptance Criteria |
| TASK_MANAGER | claude | Updates task system after a successful implementation run |

---

## Data Flow

```
  [Oracle or human] -- prepares job doc
          |
          v
  orchestrator.py  <-- reads: JOB.md (job document)
          |                   --target-repo, --epic, --request (TM mode)
          |                   --output-dir
          |
          v
    build_prompt()           constructs role prompt from:
          |                    - role instructions (roles/*.md)
          |                    - job document path
          |                    - accumulated handoff history
          |
          v
    agent_wrapper.py         spawns CLI subprocess (claude / gemini)
          |                    cwd = output_dir
          |                    env = os.environ minus CLAUDECODE
          |                    args = --output-format stream-json -p <prompt>
          |
          v
    agent CLI process        streams JSON events to stdout
          |
          v
    agent_wrapper.py         parses stream-json events
          |                    streams text to terminal in real time
          |                    writes raw events to logs/<ROLE>.log
          |                    writes raw events to execution.log
          |                    returns AgentResult(exit_code, response)
          |
          v
    parse_outcome()          extracts OUTCOME, HANDOFF, DOCS from response
          |
          v
    orchestrator loop        HANDOFF appended to handoff_history[]
          |                  DOCS triggers DOCUMENTER hook (TM mode)
          |                  OUTCOME looked up in ROUTES table
          |
          v
       next role             loop back, or halt
```

---

## DOCUMENTER Hook

In TM mode, the orchestrator runs a DOCUMENTER post-step after ARCHITECT,
IMPLEMENTOR, and TESTER — before routing to the next role. DOCUMENTER is not
a node in the ROUTES table; it is inserted automatically by the orchestrator.

The hook runs only when the triggering role emits a non-empty `DOCS:` field.
If `DOCS:` is absent or `none`, the hook is skipped for that step.

See [`routing.md`](routing.md) for the full routing table and hook details.

---

## Output Directory

All pipeline artifacts are written to `--output-dir`:

```
<output-dir>/
    execution.log       append-only log of all agent runs (role, outcome, handoff)
    logs/
        ARCHITECT.log   raw stream-json events from ARCHITECT run
        IMPLEMENTOR.log
        TESTER.log
    <generated files>   whatever the IMPLEMENTOR and TESTER produce
```

In TM mode, `current-job.txt` in the output directory holds the path to the
active job document (written by TASK_MANAGER, read by the orchestrator).

---

## References

- [`routing.md`](routing.md) — full ROUTES table, outcome values, DOCUMENTER hook
- [`job-format.md`](job-format.md) — job document structure, agent output fields
- [`decomposition.md`](decomposition.md) — multi-level decomposition, task tree navigation
- [`orchestrator.md`](orchestrator.md) — orchestrator.py internals
- [`agent_wrapper.md`](agent_wrapper.md) — agent_wrapper.py internals
- [`open-questions.md`](open-questions.md) — unresolved design questions
- [`../oracle/README.md`](../oracle/README.md) — Oracle role and outer loop coordination
- [`../roles/`](../roles/) — role prompt files loaded by build_prompt()
