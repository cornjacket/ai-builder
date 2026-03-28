# Regression Tests

Purpose: End-to-end regression tests for the ai-builder pipeline. Each test
runs the full orchestrator against a real job, verifies the generated output
with a gold test suite, and archives the run for history.

Tags: testing, regression, pipeline

---

## Tests

| Test | Pipeline mode | What it exercises |
|------|--------------|-------------------|
| [fibonacci](fibonacci/) | Simple (non-TM) | Single atomic job: ARCHITECT → IMPLEMENTOR → TESTER |
| [user-service](user-service/) | TM decomposition | Single-level decompose: one service into atomic components |
| [platform-monolith](platform-monolith/) | TM multi-level | Multi-level decompose: platform → two services → sub-components |

Each test has its own `README.md` with full specification, run instructions,
and expected pipeline routing.

---

## Common Pattern

All three tests follow the same structure:

```
tests/regression/<name>/
    gold/           committed reference tests — never visible to the pipeline
    reset.sh        wipes previous output, archives the run, sets up fresh state
    README.md       test specification and run instructions
    runs/           timestamped run archives (execution.log, task.json, README.md)
    last_run -> runs/YYYY-MM-DD-HH-MM-SS/   symlink to most recent run
```

### gold/ separation

Gold tests are committed reference tests that run after the pipeline completes.
The pipeline agent (TESTER) has no visibility into `gold/` — its working
directory is the output directory. Gold tests verify the generated code
independently against known-correct cases.

This separation ensures the pipeline cannot "cheat" by copying the gold tests
rather than deriving its own from the Acceptance Criteria.

### Run order

For every test:

1. **Reset** — `tests/regression/<name>/reset.sh`

   Archives the previous run (if any) to `runs/YYYY-MM-DD-HH-MM-SS/` with
   `execution.log`, `task.json`, and `README.md` from the Level:TOP task.
   Wipes the output and (for TM tests) target repo directories. Sets up fresh
   state for the next run.

2. **Run the pipeline** — see the test's own README for the exact command.

3. **Run the gold test** — `cd tests/regression/<name>/gold && go test -tags regression ./...`

### Run history

`reset.sh` appends a summary row to `runs/run-history.md` after each run.
Columns: run number, date, elapsed time, token counts per role
(ARCHITECT, IMPLEMENTOR, TESTER).

---

## fibonacci — Simple mode

The simplest test. Uses `--job` (non-TM) mode — a single job document fed
directly to the pipeline without a target repo or task system.

Tests the three-phase baseline: ARCHITECT fills in Design + Acceptance
Criteria, IMPLEMENTOR writes `fibonacci.go`, TESTER verifies it.

See [`fibonacci/README.md`](fibonacci/README.md) for full details.

---

## user-service — TM single-level decomposition

Exercises the full TM decomposition loop. The pipeline is given only a
high-level service specification; ARCHITECT decides the component breakdown.
DECOMPOSE_HANDLER creates the subtask tree; each component goes through its
own ARCHITECT → IMPLEMENTOR → TESTER cycle; LEAF_COMPLETE_HANDLER traverses
the tree.

See [`user-service/README.md`](user-service/README.md) for full details.

---

## platform-monolith — TM multi-level decomposition

The most complex test. A two-service monolith where one service (IAM)
itself decomposes into sub-components. Exercises the full multi-level tree
traversal: nested DECOMPOSE_HANDLER passes, INTERNAL-level integrate steps,
and a final TOP-level integrate that wires everything together.

See [`platform-monolith/README.md`](platform-monolith/README.md) for full details.
