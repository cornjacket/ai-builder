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
| `build_master_index.py` | Scans output dir for `.md` files with Purpose:/Tags: headers; writes `master-index.md` |
| `render_readme.py` | Renders `README.md` from `task.json` (TOP-level: run summary + log; non-TOP: title + subtasks) |
| `agents/` | Pluggable internal agent implementations (see [`agents/README.md`](agents/README.md)) |
| `agent-roles.md` | Canonical reference: every pipeline agent — type, inputs, outputs, valid outcomes |
| `orchestrator.md` | Code companion: inputs, outputs, internals for orchestrator.py |
| `agent_wrapper.md` | Code companion: inputs, outputs, internals for agent_wrapper.py |
| `metrics.md` | Code companion: data model, public API, and outputs for metrics.py |
| `monitoring.md` | Design document: monitoring architecture, live log, end-of-run outputs, extension points |
| `job-format.md` | Job document format and agent output field specification |
| `routing.md` | ROUTES table, outcome values per role, DOCUMENTER hook |
| `pipeline-behavior.md` | End-to-end pipeline flow: modes, Level field, tree traversal algorithm |
| `decomposition.md` | Multi-level decomposition protocol, task tree navigation |
| `open-questions.md` | Unresolved design questions |
| `recorder.py` | Record/replay support: git snapshots, manifest writing, drift detection, response loading |
| `compare_snapshot.py` | CLI for diffing a recording snapshot against the working tree |
| `record-replay.md` | User guide: how to record, replay, halt, compare snapshots, and interpret prompt drift |

---

## Pipeline Overview

The pipeline runs specialist AI agents in sequence. Each agent reads a shared
job document, does its work, and emits a structured outcome. The orchestrator
routes between agents based on that outcome.

**Two modes:**

- **Non-TM mode** (`--job`): single job document, pipeline runs once.
  Starts at ARCHITECT, terminates when TESTER passes.

- **TM mode** (`--target-repo`): Oracle-driven outer loop. The Oracle places
  the top-level task in `in-progress/` and passes its README path via `--job`,
  then invokes the orchestrator. Task READMEs are the job documents at every
  level. Internal handlers (DECOMPOSE_HANDLER, LEAF_COMPLETE_HANDLER) manage
  task state without invoking any AI model.

**Roles and agents:**

**Builder pipeline (`machines/builder/default.json`):**

| Role | Agent | Responsibility |
|------|-------|----------------|
| ARCHITECT | claude | Designs the solution (decompose or design mode); emits XML response with structured fields |
| IMPLEMENTOR | claude | Implements exactly what ARCHITECT designed; emits XML response |
| TESTER | internal | Runs `test_command` from `task.json`; returns pass/fail — impl: `agents.builder.tester.TesterAgent` |
| DECOMPOSE_HANDLER | internal | Creates pipeline subtask directories from ARCHITECT's components array; advances to first subtask — impl: `agents.builder.decompose.DecomposeAgent` |
| LEAF_COMPLETE_HANDLER | internal | Marks task complete; walks up the tree; advances to next sibling or signals DONE — impl: `agents.builder.lch.LCHAgent` |
| DOCUMENTER_POST_ARCHITECT | internal | Scans output dir for `.md` files; rebuilds README index (runs after ARCHITECT design mode) — impl: `agents.builder.documenter.DocumenterAgent` |
| DOCUMENTER_POST_IMPLEMENTOR | internal | Scans output dir for `.md` files; rebuilds README index (runs after IMPLEMENTOR) — impl: `agents.builder.documenter.DocumenterAgent` |

**Doc pipeline (`machines/doc/default.json`):**

| Role | Agent | Responsibility |
|------|-------|----------------|
| DOC_ARCHITECT | claude | Decompose mode: scan directory, identify sub-components, return components JSON. Atomic mode: read source files, write companion `.md` and `README.md`. |
| DECOMPOSE_HANDLER | internal | Same as builder pipeline; also writes `component_type: integrate` to integrate subtask's `task.json` — impl: `agents.builder.decompose.DecomposeAgent` |
| POST_DOC_HANDLER | internal | Markdown linter — checks Purpose/Tags headers, empty sections, placeholder text — impl: `agents.doc.linter.MarkdownLinterAgent` |
| LEAF_COMPLETE_HANDLER | internal | Same as builder pipeline; uses `route_on` config to emit `HANDLER_INTEGRATE_READY` for integrate subtasks — impl: `agents.builder.lch.LCHAgent` |
| DOC_INTEGRATOR | claude | Runs only at integrate nodes; reads handoff summaries, writes cross-component synthesis docs |

See [`agent-roles.md`](agent-roles.md) for full details on each agent.

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
"TESTER": { "agent": "internal", "impl": "agents.builder.tester.TesterAgent", "prompt": null, "no_history": true }
```

When `no_history: true`, the role's prompt contains only its role instructions
and the current job document — no history of what prior agents said or did.

**Use this to reduce token usage for roles that don't need prior context.**
In `default.json`, `TESTER` has `no_history: true`. `DECOMPOSE_HANDLER` and
`LEAF_COMPLETE_HANDLER` are internal (no AI model invoked) so this field is
irrelevant for them. Roles that actively reason about prior decisions
(`ARCHITECT`, `IMPLEMENTOR`) keep `no_history: false`.

The policy is fully configurable per machine file — different pipelines can
use different history strategies without touching the orchestrator source.

See [`machines/README.md`](machines/README.md) for the full field reference
and rationale.

---

## Internal Agents

Internal agents are roles whose logic runs directly in Python rather than
spawning a claude subprocess. They are declared in the machine JSON with
`"agent": "internal"` and an `"impl"` field pointing to a dotted class path:

```json
"TESTER": { "agent": "internal", "impl": "agents.builder.tester.TesterAgent", "prompt": null }
```

At startup the orchestrator calls `agents.loader.load_internal_agent(impl_path, ctx)`
which imports the module, instantiates the class (injecting `AgentContext` if
the constructor accepts one), and stores it in a dispatch table. The main loop
calls `agent.run(job_doc, output_dir, **kwargs)` — the same interface regardless
of which class is behind it.

All internal agent classes satisfy the `InternalAgent` Protocol defined in
`agents/base.py`. Custom pipelines can swap implementations without touching
orchestrator core code — just change the `"impl"` value in the machine JSON.

See [`agents/README.md`](agents/README.md) for the full package reference.

---

## Agent Knowledge Boundary

**AI agents (ARCHITECT, IMPLEMENTOR, TESTER) must never have knowledge of:**
- Task management scripts (`new-pipeline-subtask.sh`, `complete-task.sh`, etc.)
- `task.json` — its structure, fields, or location
- `last-job.json` — how the pipeline advances between tasks (written after each stage)
- Any orchestrator internals

**AI agents know only:**
- The job document (`README.md`) — provided via path in the prompt
- Target-repo build/test commands — from `## Suggested Tools` in the job doc

This boundary is enforced structurally:
1. Agent prompts (`machines/builder/roles/*.md`) contain no script names, no
   `task.json` references, and no `last-job.json` references.
2. `CLAUDE.md` is not injected into agent prompts. Agents run with
   `cwd=/tmp` (not the repo root), so CLAUDE.md is not loaded.
3. DECOMPOSE_HANDLER and LEAF_COMPLETE_HANDLER are **internal** (no AI model
   invoked) — the only roles that previously needed script knowledge are now
   pure Python. No agent prompt covers these roles.

**Rule for future prompt edits:** if a proposed change to any role prompt
file would require an AI agent to know about scripts, task.json fields, or
pipeline internals, the change is wrong. The orchestrator mediates all
pipeline mechanics; agents read and write only the job doc prose.

---

---

## Submitting a Pipeline Build Run (TM mode)

The orchestrator validates that the pipeline entry point is a **PIPELINE-SUBTASK
with `Level: TOP`**. Pointing it at a USER-TASK is an error.

```bash
# 1. Create a build entry point under the user-task
README=$(project/tasks/scripts/new-pipeline-build.sh \
    --epic main --folder in-progress --parent <user-task-name> \
    | grep "^README:" | awk '{print $2}')

# 2. Fill in Goal and Context in the created README, then run the orchestrator
python3 ai-builder/orchestrator/orchestrator.py \
    --job         "$README" \
    --target-repo <target-repo> \
    --output-dir  <output-dir> \
    --epic        main \
    --state-machine ai-builder/orchestrator/machines/builder/default.json
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

In TM mode, `last-job.json` in the output directory records the active task
README path after each stage advance. Written by the orchestrator whenever a
handler emits `HANDLER_SUBTASKS_READY`. Used by `--resume` to restore the
active job without requiring `--job`.

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
