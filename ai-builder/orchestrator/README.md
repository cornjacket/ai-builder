# ai-builder pipeline

The orchestrator core. Drives a multi-role AI pipeline that takes a job
document from input to tested implementation through specialist agents.

---

## Files

| File | Description |
|------|-------------|
| `orchestrator.py` | Main pipeline loop: routes between roles, manages state, parses outcomes |
| `agent_wrapper.py` | Spawns agent CLI subprocesses, streams output, returns results |
| `metrics.py` | Captures per-invocation timing and token usage; writes run-summary.md and run-metrics.json |
| `orchestrator.md` | Code companion: inputs, outputs, internals for orchestrator.py |
| `agent_wrapper.md` | Code companion: inputs, outputs, internals for agent_wrapper.py |
| `metrics.md` | Code companion: data model, public API, and outputs for metrics.py |
| `monitoring.md` | Design document: monitoring architecture, live log, end-of-run outputs, extension points |
| `job-format.md` | Job document format and agent output field specification |
| `routing.md` | ROUTES table, outcome values per role, DOCUMENTER hook |
| `pipeline-behavior.md` | End-to-end pipeline flow: modes, Level field, tree traversal algorithm |
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

- **TM mode** (`--target-repo`): Oracle-driven outer loop. The Oracle places
  the top-level task in `in-progress/` and writes its README path to
  `current-job.txt`, then invokes the orchestrator. Task READMEs are the job
  documents at every level — DECOMPOSE_HANDLER fills in Goal/Context for
  component subtasks and updates `current-job.txt` to point at the next task README.

**Roles and agents:**

| Role | Agent | Responsibility |
|------|-------|----------------|
| ARCHITECT | claude | Designs the solution; fills Design + Acceptance Criteria |
| IMPLEMENTOR | claude | Implements exactly what ARCHITECT designed |
| TESTER | claude | Verifies implementation against Acceptance Criteria |
| DECOMPOSE_HANDLER     | claude | Creates subtasks from ARCHITECT's component table; advances pipeline to first subtask |
| LEAF_COMPLETE_HANDLER | claude | Marks task complete, walks up the tree, advances to next sibling or signals DONE |

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
          |                  OUTCOME looked up in ROUTES table
          |
          v
       next role             loop back, or halt
```

---

## Configuring Handoff History Per Role

Each role can be configured to receive or suppress the accumulated handoff
history via the `no_history` field in the state machine JSON:

```json
"TESTER": { "agent": "claude", "prompt": "roles/TESTER.md", "no_history": true }
```

When `no_history: true`, the role's prompt contains only its role instructions
and the current job document — no history of what prior agents said or did.

**Use this to reduce token usage for roles that don't need prior context.**
In `default.json`, `TESTER`, `DECOMPOSE_HANDLER`, and `LEAF_COMPLETE_HANDLER`
all have `no_history: true`. Roles that actively reason about prior decisions
(`ARCHITECT`, `IMPLEMENTOR`) keep `no_history: false`.

The policy is fully configurable per machine file — different pipelines can
use different history strategies without touching the orchestrator source.

See [`machines/README.md`](machines/README.md) for the full field reference
and rationale.

---

## DOCUMENTER Hook *(planned, not yet implemented)*

In TM mode, the orchestrator will run a DOCUMENTER post-step after ARCHITECT,
IMPLEMENTOR, and TESTER — before routing to the next role. DOCUMENTER is not
a node in the ROUTES table; it will be inserted automatically by the orchestrator.

The hook will run only when the triggering role emits a non-empty `DOCS:` field.
If `DOCS:` is absent or `none`, the hook will be skipped for that step.

This hook is not present in the current `orchestrator.py`. See
[`routing.md`](routing.md) for the intended design.

---

## Submitting a Pipeline Build Run (TM mode)

The orchestrator validates that the pipeline entry point is a **PIPELINE-SUBTASK
with `Level: TOP`**. Pointing it at a USER-TASK is an error.

```bash
# 1. Create a build entry point under the user-task
README=$(project/tasks/scripts/new-pipeline-build.sh \
    --epic main --folder in-progress --parent <user-task-name> \
    | grep "^README:" | awk '{print $2}')

# 2. Fill in Goal and Context in the created README, then register it
<target-repo>/project/tasks/scripts/set-current-job.sh \
    --output-dir <output-dir> "$README"

# 3. Run the orchestrator
python3 ai-builder/orchestrator/orchestrator.py \
    --target-repo <target-repo> \
    --output-dir  <output-dir> \
    --epic        main \
    --state-machine ai-builder/orchestrator/machines/default.json
```

---

## Output Directory

All pipeline artifacts are written to `--output-dir`:

```
<output-dir>/
    execution.log       append-only log of all agent runs (role, outcome, handoff)
    run-summary.md      human-readable run summary (timing, tokens, per-role totals)
    run-metrics.json    machine-readable run metrics (same data as run-summary.md)
    logs/
        ARCHITECT.log   raw stream-json events from ARCHITECT run
        IMPLEMENTOR.log
        TESTER.log
    <generated files>   whatever the IMPLEMENTOR and TESTER produce
```

In TM mode, `current-job.txt` in the output directory holds the absolute path
to the active task README (the job document). Written by Oracle at startup and
by LEAF_COMPLETE_HANDLER via `set-current-job.sh` when advancing to the next task.

The `run-summary.md` content is also appended as a `## Run Summary` section to
the Level:TOP pipeline-subtask README at the end of the run.

---

## References

- [`routing.md`](routing.md) — full ROUTES table, outcome values, DOCUMENTER hook
- [`job-format.md`](job-format.md) — job document structure, agent output fields
- [`pipeline-behavior.md`](pipeline-behavior.md) — end-to-end pipeline flow, Level field, tree traversal
- [`decomposition.md`](decomposition.md) — multi-level decomposition, task tree navigation
- [`orchestrator.md`](orchestrator.md) — orchestrator.py internals
- [`agent_wrapper.md`](agent_wrapper.md) — agent_wrapper.py internals
- [`metrics.md`](metrics.md) — metrics.py internals
- [`monitoring.md`](monitoring.md) — monitoring system design and extension guide
- [`open-questions.md`](open-questions.md) — unresolved design questions
- [`../roles/`](../roles/) — role prompt files loaded by build_prompt()
