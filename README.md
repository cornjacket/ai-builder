# ai-builder

An automated software development pipeline that takes a specification from
design to tested implementation using specialist AI agents. A human or Oracle
submits a job; the pipeline decomposes it, implements each component, tests
it, and reassembles the whole — without human involvement between steps.

---

## Getting Started

This repository uses a git worktree workspace layout. To set up on a new
machine, clone into a bootstrap directory and run the setup script:

```bash
cd ~/Go/src/github.com/cornjacket          # or wherever you keep your repos
git clone git@github.com:cornjacket/ai-builder.git ai-builder-bootstrap
bash ai-builder-bootstrap/bootstrap/setup-workspace.sh
rm -rf ai-builder-bootstrap
```

This creates:
```
ai-builder/
    .bare/    git object store
    .git      pointer to .bare/
    main/     main branch worktree  ← work here
```

All day-to-day work happens inside `main/` (or a feature worktree). See
[`bootstrap/README.md`](bootstrap/README.md) for branch worktree management.

---

## Repository Layout

```
ai-builder/         Orchestrator, state machines, role prompts, companion docs
ai-builder/orchestrator/machines/builder/  Builder pipeline machine + role prompts
ai-builder/orchestrator/machines/doc/      Doc pipeline machine + role prompts
bootstrap/          Workspace setup and worktree management scripts
target/             Bootstrap scripts for setting up a target repository
tests/
    regression/     Gold tests for full pipeline runs; infra smoke test
    unit/           Python unit tests for orchestrator modules
project/            Task management system for this repo's own development
sandbox/            Untracked scratch space for pipeline runs and experiments
docs/               Design notes and reference documents
```

---

## How the Pipeline Works

The orchestrator drives specialist AI agents in sequence. Each agent reads a
shared job document, does its work, and emits a structured outcome. The
orchestrator routes between agents based on that outcome.

The pipeline is configured by a **machine JSON file** that defines the roles,
their agent types, and the full transition table. Different machine files
implement different pipelines — the orchestrator core is unchanged.

**Builder pipeline** (design → implement → test):
```
[Oracle] writes job doc → orchestrator.py
    → ARCHITECT    designs the solution; fills Design + Acceptance Criteria
    → IMPLEMENTOR  implements exactly what ARCHITECT designed
    → TESTER       verifies implementation against Acceptance Criteria
    → (repeat for each component when the task is decomposed)
    → DONE
```

**Doc pipeline** (traverse source tree → generate documentation):
```
[Oracle] writes job doc → orchestrator.py
    → DOC_ARCHITECT   decomposes or documents a source directory
    → POST_DOC_HANDLER  lints the generated .md files
    → LEAF_COMPLETE_HANDLER → DOC_INTEGRATOR (at composite nodes)
    → (repeat for each sub-directory; synthesise at each composite node)
    → DONE
```

For complex tasks, the pipeline traverses a subtask tree depth-first. See
[`ai-builder/orchestrator/pipeline-behavior.md`](ai-builder/orchestrator/pipeline-behavior.md)
for the full traversal algorithm.

---

## Two Modes

| Mode | Flag | Use when |
|------|------|----------|
| **Non-TM** | `--job <path>` | Running the pipeline against a single hand-written job document |
| **TM** | `--target-repo <path>` | Running against a target repository with the full task management system; supports multi-level decomposition |

TM mode requires the entry point to be a `PIPELINE-SUBTASK` with `Level: TOP`.
Use `new-pipeline-build.sh` to create one (see Quick Start below).

---

## Pipelines

| Machine file | Purpose |
|--------------|---------|
| `machines/builder/default.json` | Build pipeline — ARCHITECT → IMPLEMENTOR → TESTER |
| `machines/doc/default.json` | Doc pipeline — traverses a source tree and generates companion `.md` files |

Pass any machine file with `--state-machine <file>`. See
[`ai-builder/orchestrator/machines/README.md`](ai-builder/orchestrator/machines/README.md)
for the machine JSON format reference.

---

## Quick Start: Non-TM Mode

```bash
python3 ai-builder/orchestrator/orchestrator.py \
    --job         /path/to/job.md \
    --output-dir  /path/to/output
```

The job document must describe the Goal, Context, and any Acceptance Criteria.
The orchestrator writes all artifacts to `--output-dir`.

---

## Quick Start: TM Mode

```bash
# 1. Set up a fresh target repository
target/setup-project.sh  /path/to/target-repo --epic main
target/init-claude-md.sh /path/to/target-repo

# 2. Create the pipeline entry point
SCRIPTS=/path/to/target-repo/project/tasks/scripts
README=$($SCRIPTS/new-pipeline-build.sh \
    --epic main --folder in-progress --parent <user-task-name> \
    | grep "^README:" | awk '{print $2}')

# 3. Fill in Goal and Context in $README, then register it
$SCRIPTS/set-current-job.sh --output-dir /path/to/output "$README"

# 4. Run the orchestrator
python3 ai-builder/orchestrator/orchestrator.py \
    --target-repo  /path/to/target-repo \
    --output-dir   /path/to/output \
    --epic         main \
    --state-machine ai-builder/orchestrator/machines/builder/default.json
```

See [`ai-builder/orchestrator/README.md`](ai-builder/orchestrator/README.md)
for the full command reference and output directory layout.

---

## Task Management

This repository uses a structured task system to track all development work.
All tasks are tracked under [`project/tasks/`](project/tasks/).

```bash
# Show outstanding work sorted by priority
project/tasks/scripts/list-tasks.sh --epic main --folder backlog    --sort-priority
project/tasks/scripts/list-tasks.sh --epic main --folder draft      --sort-priority
project/tasks/scripts/list-tasks.sh --epic main --folder in-progress --sort-priority
```

See [`project/tasks/README.md`](project/tasks/README.md) for the full task
management documentation and script reference.

---

## Regression Tests

Regression tests live under [`tests/regression/`](tests/regression/). Each
test has a `reset.sh` script that sets up the sandbox and a `gold/` directory
with the acceptance tests.

```bash
# Run the infra smoke test first (validates the framework, ~10s, no pipeline needed)
cd tests/regression
go test -v ./infra-smoke/smoke/

# Run a full regression test (requires a completed pipeline run)
tests/regression/user-service/reset.sh          # set up sandbox
# ... run the orchestrator (see reset.sh output for the command) ...
cd tests/regression/user-service/gold && go test -tags regression ./...
```

See [`tests/regression/how-to-write-a-regression-test.md`](tests/regression/how-to-write-a-regression-test.md)
for instructions on adding a new regression test.

---

## Key Design Documents

| Document | What it covers |
|----------|---------------|
| [`ai-builder/orchestrator/README.md`](ai-builder/orchestrator/README.md) | Orchestrator overview, data flow, TM mode, output directory layout |
| [`ai-builder/orchestrator/pipeline-behavior.md`](ai-builder/orchestrator/pipeline-behavior.md) | End-to-end pipeline flow, Level field, tree traversal algorithm |
| [`ai-builder/orchestrator/decomposition.md`](ai-builder/orchestrator/decomposition.md) | Multi-level decomposition protocol, task tree navigation |
| [`ai-builder/orchestrator/monitoring.md`](ai-builder/orchestrator/monitoring.md) | Metrics architecture, live execution log, end-of-run outputs |
| [`ai-builder/orchestrator/routing.md`](ai-builder/orchestrator/routing.md) | ROUTES table, outcome values, DOCUMENTER hook |
| [`CLAUDE.md`](CLAUDE.md) | Instructions for AI agents working in this repository |
