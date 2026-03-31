# Theory of Operation

Purpose: Unified narrative describing how the ai-builder pipeline works end to
end — from Oracle job submission through decomposition, implementation, testing,
and completion. Covers both operating modes, data flows, and operational concerns.
Tags: orchestrator, pipeline, architecture

This document is the entry point for understanding the pipeline as a whole.
Where detailed specifications already exist they are referenced rather than
duplicated. See the [file index in the README](README.md) for the full doc tree.

---

## What the Pipeline Is

The pipeline takes a job — a natural-language description of a software
component — and produces tested, working source code. It does this by routing
a sequence of specialist AI and internal agents, each responsible for one
concern:

| Agent | Concern |
|-------|---------|
| ARCHITECT | Design: decompose a complex job or produce design + acceptance criteria for an atomic one |
| IMPLEMENTOR | Code: write source files that satisfy the design |
| TESTER | Verify: run the test command and report pass/fail |
| DECOMPOSE_HANDLER | Orchestration: create subtask directories from ARCHITECT's component list |
| LEAF_COMPLETE_HANDLER | Orchestration: advance to the next task after a component passes |
| DOCUMENTER_POST_ARCHITECT/IMPLEMENTOR | Documentation: index `.md` files written during design/implementation |

The orchestrator (`orchestrator.py`) drives the loop. It builds each agent's
prompt from `task.json` fields, invokes the agent, parses the structured XML
response (or plain `OUTCOME:`/`HANDOFF:` lines for internal agents), routes to
the next agent, and updates shared state.

---

## Two Operating Modes

### Simple Mode (`--job`)

A single job document is given directly. No target repository, no task system,
no decomposition. The pipeline runs exactly once:

```
ARCHITECT → DOCUMENTER_POST_ARCHITECT → IMPLEMENTOR
         → DOCUMENTER_POST_IMPLEMENTOR → TESTER → halt
```

Suited for atomic tasks where a human provides the full specification upfront.
This is the mode used by the fibonacci regression test.

### TM Mode (`--target-repo`)

The pipeline is pointed at a target repository containing a task management
system. The Oracle has placed a `PIPELINE-SUBTASK` with `Level: TOP` in
`in-progress/` and written `current-job.txt` in the run directory to point
to it. The pipeline then drives the full decomposition tree.

When a job is composite, ARCHITECT decomposes it; DECOMPOSE_HANDLER creates
subtasks; each component goes through its own design/implement/test cycle;
LEAF_COMPLETE_HANDLER walks the tree until `HANDLER_ALL_DONE`.

---

## Data Structures

### `task.json`

Every pipeline-subtask directory contains a `task.json`. This is the primary
communication medium between the Oracle, the orchestrator, and the agents.
Agents do not read each other's `task.json` directly — the orchestrator reads
it and injects fields inline into prompts.

| Field | Written by | Consumed by | Notes |
|-------|-----------|-------------|-------|
| `goal` | Oracle / DECOMPOSE_HANDLER | Orchestrator → ARCHITECT, IMPLEMENTOR prompt | Component description (description field from parent's XML response) |
| `context` | Oracle / DECOMPOSE_HANDLER | Orchestrator → ARCHITECT, IMPLEMENTOR prompt | Ancestry chain: `### Level N — <task>` entries |
| `complexity` | Oracle / DECOMPOSE_HANDLER | Orchestrator (mode selection) | `—`, `atomic`, or `composite` |
| `level` | Oracle / DECOMPOSE_HANDLER | Orchestrator → ARCHITECT prompt | `TOP` or `INTERNAL` — controls integrate test scope |
| `output_dir` | Oracle / DECOMPOSE_HANDLER | Orchestrator | Where to write generated files |
| `depth` | DECOMPOSE_HANDLER | — | Tree depth (informational) |
| `last-task` | DECOMPOSE_HANDLER | `advance-pipeline.sh` | `true` on the integrate component; triggers upward walk |
| `design` | Orchestrator (from ARCHITECT XML) | Orchestrator → IMPLEMENTOR prompt | Full design prose |
| `acceptance_criteria` | Orchestrator (from ARCHITECT XML) | Orchestrator → IMPLEMENTOR prompt | Numbered acceptance criteria |
| `test_command` | Orchestrator (from ARCHITECT XML) | TESTER internal agent | Exact shell command to run tests |
| `documents_written` | Orchestrator (from ARCHITECT/IMPLEMENTOR XML) | DOCUMENTER internal agents | Skip flag for DOCUMENTER |
| `execution_log` | Orchestrator (after every invocation) | `render_readme.py` | Per-invocation records: role, tokens, timing, outcome |
| `run_summary` | Orchestrator (at run end) | `render_readme.py` | Elapsed time, start/end, total tokens |

The orchestrator also holds all design fields in an in-memory `task_state`
dict to avoid disk round-trips. `task.json` writes are for persistence
(resume after interruption) only.

### Sidecar files (`--run-dir`)

Coordination files for a single pipeline run. By default they go into
`--output-dir`; `--run-dir` separates them to allow concurrent runs.

| File | Written by | Read by |
|------|-----------|---------|
| `current-job.txt` | `set-current-job.sh` / `on-task-complete.sh` | Orchestrator main loop |
| `execution.log` | Orchestrator | Humans, archived by `reset.sh` |
| `handoff-state.json` | Orchestrator | Orchestrator on `--resume` |
| `last-job.json` | `on-task-complete.sh` | — (legacy; may be removed) |

### Handoff history and frame stack

`handoff_history` is a list of `[ROLE] <handoff text>` strings, accumulated
across every agent invocation in a run. It is injected into every AI agent
prompt as `## Handoff Notes from Previous Agents`. Internal agents are
excluded (they don't receive a prompt).

`frame_stack` tracks the nesting context for multi-level decomposition. Each
entry represents one decomposition level. Both are persisted to
`handoff-state.json` and restored on `--resume`.

---

## The Two-Tree Structure

In TM mode, the pipeline maintains two parallel directory trees:

```
Target repo (task tree)                    Output directory (code tree)
─────────────────────────────────────────  ────────────────────────────────────────
project/tasks/main/in-progress/            sandbox/user-service-output/
  USER-TASK  49352f-user-service/            ↑ build-1.output_dir
    PIPELINE-SUBTASK build-1/
      task.json  (Level:TOP, goal, context)
      README.md  (rendered by orchestrator)
      PIPELINE-SUBTASK store/                internal/store/
        task.json  (complexity:atomic,         ↑ store.output_dir
                    output_dir:…/store)        store.go
        README.md                             store_test.go
      PIPELINE-SUBTASK handlers/             README.md (ARCHITECT)
        task.json  (output_dir:…/handlers)
        README.md                           internal/handlers/
      PIPELINE-SUBTASK integrate/             handlers.go
        task.json  (last-task:true,           handlers_test.go
                    output_dir:…/build-1)    README.md (ARCHITECT)
                                           main.go           ← integrate writes here
                                           go.mod
                                           master-index.md   ← built by DOCUMENTER
                                           README.md         ← rendered from task.json
```

Key relationships:
- Every `PIPELINE-SUBTASK` has an `output_dir` in `task.json` pointing to its
  subtree in the code tree.
- `source_dir` in ARCHITECT's decompose response drives placement: `store` →
  `<parent_output_dir>/internal/store`; `integrate` → `<parent_output_dir>` (`.`).
- The task tree and code tree are owned by separate repositories — the task
  system lives in the target repo; generated code lives in the output dir.
- Completed subtasks are renamed `X-<name>` in the task tree. The code tree
  is never renamed.

---

## Simple Mode: End-to-End Flow

```
  Oracle
    │ python3 orchestrator.py --job spec.md --output-dir out/
    │                         --state-machine machines/builder/simple.json
    ▼
  Orchestrator reads spec.md → creates task.json with goal from README
    │
    ▼
  ┌──────────────────────────────────────────────────────┐
  │  ARCHITECT                                           │
  │  Receives: Goal, Context, Complexity, output_dir     │
  │  Writes:   README.md to output_dir                   │
  │  Emits:    <response>                                │
  │              <outcome>ARCHITECT_DESIGN_READY</outcome>│
  │              <design>...</design>                    │
  │              <acceptance_criteria>...</acceptance_criteria>│
  │              <test_command>cd out && go test...</test_command>│
  │              <documents_written>true</documents_written>│
  │            </response>                               │
  └──────────────────────────────────────────────────────┘
    │ orchestrator stores design/ac/test_command in task.json + task_state
    ▼
  DOCUMENTER_POST_ARCHITECT
    │ scans output_dir for *.md with Purpose:/Tags: headers
    │ rebuilds README index in output_dir/README.md
    ▼
  ┌──────────────────────────────────────────────────────┐
  │  IMPLEMENTOR                                         │
  │  Receives: Goal, Design, Acceptance Criteria,        │
  │            Test Command, output_dir (all inline)     │
  │  Writes:   source files + companion .md to output_dir│
  │  Emits:    <response>                                │
  │              <outcome>IMPLEMENTOR_IMPLEMENTATION_DONE</outcome>│
  │              <handoff>...</handoff>                  │
  │              <documents_written>false</documents_written>│
  │            </response>                               │
  └──────────────────────────────────────────────────────┘
    │
    ▼
  DOCUMENTER_POST_IMPLEMENTOR  (no-op if documents_written=false)
    │
    ▼
  TESTER
    │ reads test_command from task.json
    │ runs subprocess
    │ emits OUTCOME: TESTER_TESTS_PASS
    ▼
  halt (exit 0)
```

---

## TM Mode: Single-Level Decomposition

```
  Oracle
    │ sets up target repo, creates build-1 (Level:TOP), writes current-job.txt
    │ python3 orchestrator.py --target-repo target/ --output-dir out/
    │                         --state-machine machines/builder/default.json
    ▼
  ┌───────────────────────────────────────────────────────────┐
  │  ARCHITECT (decompose mode — Complexity: —)               │
  │  Receives: Goal, Context, Complexity=—, Level=TOP         │
  │  Writes:   README.md to out/ (overview of service)        │
  │  Emits:    <response>                                     │
  │              <outcome>ARCHITECT_DECOMPOSITION_READY</outcome>│
  │              <components>                                 │
  │                <component><name>store</name>...</component>│
  │                <component><name>handlers</name>...</component>│
  │                <component><name>integrate</name>...</component>│
  │              </components>                               │
  │            </response>                                   │
  └───────────────────────────────────────────────────────────┘
    │
    ▼
  DECOMPOSE_HANDLER
    │ for each component:
    │   new-pipeline-subtask.sh → creates task dir in target repo
    │   writes goal/context/complexity/depth/output_dir into task.json
    │   creates output subdirectory (keyed by source_dir)
    │   seeds README.md placeholder
    │ set-current-job.sh → points current-job.txt at store/README.md
    │ emits OUTCOME: HANDLER_SUBTASKS_READY
    ▼
  ┌─── for each component (store, handlers, integrate) ────────┐
  │                                                            │
  │  ARCHITECT (design mode — Complexity: atomic)             │
  │    writes README.md + optional named docs to output_dir   │
  │    emits ARCHITECT_DESIGN_READY with design fields        │
  │    orchestrator stores design fields in task.json         │
  │         ▼                                                 │
  │  DOCUMENTER_POST_ARCHITECT                                │
  │         ▼                                                 │
  │  IMPLEMENTOR                                              │
  │    writes source files to output_dir                      │
  │    emits IMPLEMENTOR_IMPLEMENTATION_DONE                  │
  │         ▼                                                 │
  │  DOCUMENTER_POST_IMPLEMENTOR                              │
  │         ▼                                                 │
  │  TESTER                                                   │
  │    runs test_command from task.json                       │
  │    emits TESTER_TESTS_PASS                                │
  │         ▼                                                 │
  │  LEAF_COMPLETE_HANDLER                                    │
  │    on-task-complete.sh:                                   │
  │      complete-task.sh → marks [x] in parent              │
  │      Last-task=false? → NEXT <next-sibling>              │
  │      Last-task=true?  → walk up → parent is USER-TASK    │
  │                         → emit TOP_RENAME_PENDING        │
  │                         → emit DONE                      │
  │    emits HANDLER_SUBTASKS_READY  (or HANDLER_ALL_DONE)   │
  └────────────────────────────────────────────────────────────┘
    │ (on HANDLER_ALL_DONE)
    ▼
  Post-completion flow (see below)
  halt (exit 0)
```

---

## TM Mode: Multi-Level Decomposition

When ARCHITECT encounters a `composite` component, it decomposes it rather
than designing it. DECOMPOSE_HANDLER creates a nested subtask tree. The
pipeline recurses without the orchestrator tracking depth explicitly — depth
is encoded in the task tree and `last-task` field.

```
build-1 (TOP, Complexity:—)
  │
  ├── metrics (composite)   ← ARCHITECT decomposes
  │     ├── store (atomic)
  │     ├── handlers (atomic)
  │     └── integrate (INTERNAL, last-task:true)
  │
  ├── iam (composite)       ← ARCHITECT decomposes
  │     ├── lifecycle (atomic)
  │     ├── authz (atomic)
  │     └── integrate (INTERNAL, last-task:true)
  │
  └── integrate (TOP, last-task:true)
```

Tree traversal proceeds depth-first, left-to-right. When `integrate` at an
INTERNAL level completes:
- `advance-pipeline.sh` sees `last-task=true`
- walks up to the parent (e.g. `iam`)
- parent is a PIPELINE-SUBTASK → marks it `[x]`, continues up
- finds next sibling at the grandparent level (`metrics` → done, advance to `integrate`)

When `integrate` at the TOP level completes:
- walks up to the build-1 parent
- build-1's parent is the USER-TASK (human boundary)
- emits `TOP_RENAME_PENDING build-1` and `DONE`
- orchestrator captures the rename and defers it

See [`pipeline-behavior.md`](pipeline-behavior.md) for the full traversal
algorithm pseudocode.

---

## Post-Completion Flow

When `HANDLER_ALL_DONE` is received, the orchestrator runs these steps in
order before halting. The order matters: steps use `task.json` paths that
become invalid after the rename.

```
1. Write final metrics to Level:TOP task.json
   (execution_log entries + run_summary: elapsed, tokens per role)

2. Render README.md for Level:TOP task
   render_readme.py: title, run_summary table, execution_log table, subtask list

3. Rebuild master-index.md in output_dir
   build_master_index.py: walk output_dir for *.md with Purpose:/Tags: headers

4. Apply deferred TOP rename
   build-1/ → X-build-1/
   (task.json paths are now stale — no more writes after this)

5. halt (exit 0)
```

The rename is deferred (TOP_RENAME_PENDING protocol) because the orchestrator
needs to write to `task.json` in steps 1–3, and the path `build-1/task.json`
becomes `X-build-1/task.json` after the rename. Step 4 is always last.

---

## Agent Output Format

AI agents (ARCHITECT, IMPLEMENTOR) emit a `<response>` XML block as the final
content of their response. XML self-delimiting tags allow design prose, shell
commands, and code blocks to appear inside field values without escaping.

```xml
<response>
  <outcome>ARCHITECT_DESIGN_READY</outcome>
  <handoff>one paragraph for downstream agents</handoff>
  <documents_written>true</documents_written>
  <design>
## Design

The store uses sync.RWMutex...
  </design>
  <acceptance_criteria>
1. go test ./... passes.
2. Concurrent reads do not block each other.
  </acceptance_criteria>
  <test_command>cd /path/to/output && go test ./...</test_command>
</response>
```

Internal agents emit plain `OUTCOME:`/`HANDOFF:` lines. The orchestrator
parser tries XML first, then JSON (backward compatibility), then plain lines.

See [`agent-roles.md`](agent-roles.md) for full details on each agent's
inputs, outputs, and valid outcomes.

---

## State Machine

The routing table is defined in a JSON file loaded at startup. Two built-in
configurations:

- `machines/builder/simple.json` — non-TM (single-step) mode
- `machines/builder/default.json` — TM mode with full decomposition support

See [`machines/README.md`](machines/README.md) for the format specification
and [`routing.md`](routing.md) for the full ROUTES tables.

---

## Operational Concerns

### Loop detection

The orchestrator maintains a sliding window of 8 `(role, job_doc_path)` pairs.
If the same pair recurs within the window, the pipeline halts with an error.
This catches cross-role loops (e.g. ARCHITECT → DECOMPOSE_HANDLER → ARCHITECT
cycling on the same job doc due to a bug in tree navigation).

### Resume

`--resume` restarts a stalled pipeline from the current `current-job.txt`
position. On startup it loads `handoff-state.json` to restore `handoff_history`
and `frame_stack`, then seeds the execution log with the prior run's entries
so the resumed run has continuity.

`--clean-resume` additionally deletes output files newer than the last
completed-component marker before restarting, cleaning up a partial ARCHITECT
or IMPLEMENTOR run.

See [`orchestrator.md`](orchestrator.md) for the full CLI reference.

### Run directory separation

`--run-dir DIR` separates coordination sidecar files from generated code
output. This allows two pipeline runs against different tasks to share an
`--output-dir` root without their `current-job.txt` and `execution.log` files
colliding. When omitted, sidecar files go into `--output-dir`.

### Monitoring and metrics

After every agent invocation, the orchestrator records tokens in/out/cached,
elapsed time, role, and outcome in `execution_log` in the Level:TOP `task.json`.
The live Level:TOP README is re-rendered after each invocation so a human
watching the run sees live progress.

At run end, `run_summary` (elapsed, totals per role) is written. See
[`monitoring.md`](monitoring.md) for the full metrics schema and outputs.

---

## Regression Tests

Three regression tests cover the pipeline modes described above. They follow
a common pattern: `reset.sh` archives the previous run and sets up fresh
state; the pipeline runs; a gold test suite verifies the output independently.

| Test | Mode | What it covers |
|------|------|----------------|
| fibonacci | Simple | Three-phase baseline: ARCHITECT → IMPLEMENTOR → TESTER |
| user-service | TM single-level | Full decomposition loop, LEAF_COMPLETE_HANDLER tree walk |
| platform-monolith | TM multi-level | Nested decomposition, INTERNAL vs TOP integrate, full tree traversal |

See [`tests/regression/README.md`](../../tests/regression/README.md) for the
full test index and run instructions. Individual test specs:
- [`tests/regression/fibonacci/README.md`](../../tests/regression/fibonacci/README.md)
- [`tests/regression/user-service/README.md`](../../tests/regression/user-service/README.md)
- [`tests/regression/platform-monolith/README.md`](../../tests/regression/platform-monolith/README.md)
