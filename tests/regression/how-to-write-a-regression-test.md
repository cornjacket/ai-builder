# How to Write a Regression Test

Regression tests verify that the ai-builder **pipeline** behaves correctly —
not just that the generated code works. Each test exercises a specific pipeline
capability (flat atomic, single-level decomposition, multi-level decomposition,
tree traversal, etc.) and uses gold tests to independently confirm the output
matches the original spec.

---

## 1. Purpose

A regression test has two goals:

1. **Pipeline correctness** — the pipeline routes correctly, DECOMPOSE_HANDLER
   creates the right task structure, agents hand off cleanly, and
   `HANDLER_ALL_DONE` fires at the right time.

2. **Output correctness** — the generated code actually implements the spec.
   This is verified by gold tests, which are independent of whatever tests the
   pipeline's TESTER agent writes.

Every regression test should document which pipeline capability it exercises
in its README.

---

## 2. Directory Structure

Each regression test lives under `tests/regression/<test-name>/` with this
standard layout:

```
tests/regression/<test-name>/
    reset.sh          # resets to initial state; creates sandbox/ target repo
    build-spec.md     # the spec written into the parent USER-TASK README on each reset
    gold/
        go.mod        # or equivalent
        gold_test.go  # behavioural gold tests (build tag: regression)
    README.md         # test documentation, architecture diagram, run instructions
```

`build-spec.md` is the authoritative spec for TM-mode tests. It is written into
the parent USER-TASK README by `reset.sh`, and `new-pipeline-build.sh` reads
`goal` and `context` from the parent to populate the pipeline-subtask's
`task.json`. This tests the full Oracle flow — spec lives in the USER-TASK,
pipeline picks it up from there.

For non-TM tests (e.g. `fibonacci/`), the job document is a standalone `.md`
file committed directly to the test directory and passed via `--job`.

No generated output is committed. All pipeline output goes to `sandbox/` (see §4).

---

## 3. reset.sh Contract

Every `reset.sh` must perform these steps in order:

1. **Save the previous run** to `last_run/` (see §3a).
2. **Wipe and recreate** the target repo at `sandbox/<test-name>-target/`.
3. **Install the task system** using `target/setup-project.sh` and
   `target/init-claude-md.sh`.
4. **Create a USER-TASK** (Oracle-owned pipeline boundary) in `in-progress/`
   using `new-user-task.sh`. This is the human-owned node the pipeline must
   not traverse above.
5. **Write the spec** into the USER-TASK README (`build-spec.md` copied to
   the parent task's README). The spec lives in the Oracle-owned task, which
   exists before the pipeline-subtask is created.
6. **Create a PIPELINE-SUBTASK** entry point under the USER-TASK using
   `new-pipeline-build.sh`. The script reads `goal` and `context` from the
   parent USER-TASK README and writes them into the new subtask's `task.json`
   — no separate step needed. Complexity is left as `—` to trigger ARCHITECT
   decompose mode.
7. **Point `current-job.txt`** at the PIPELINE-SUBTASK README using
   `set-current-job.sh --output-dir <sandbox-output-dir>`.
8. **Wipe the output dir** — `rm -rf` the entire output dir and recreate it
   empty. This removes all previously generated code, logs, and artifacts so
   the pipeline starts from a clean slate and agents don't waste tokens
   reading or rewriting stale output.

Print the pipeline run command and gold test command at the end.

### Sandbox paths

| Directory | Purpose |
|-----------|---------|
| `sandbox/<test-name>-target/` | Fresh target repo (task system + generated code) |
| `sandbox/<test-name>-output/` | Pipeline output dir (execution.log, logs/, current-job.txt) |

**Never use `/tmp/`** for target repos or output dirs. Sandbox paths are
tracked in git (gitignored content, committed structure) and survive sessions.

---

## 3a. Last Run Preservation

`reset.sh` automatically saves the previous run's artifacts to
`tests/regression/<test-name>/last_run/` before wiping. This directory is
gitignored — it is a local workspace artifact only.

### What is saved

| File | Source | Always present |
|------|--------|----------------|
| `execution.log` | `sandbox/<test-name>-output/` | yes (triggers save) |
| `run-metrics.json` | `sandbox/<test-name>-output/` | only on normal completion |
| `run-summary.md` | `sandbox/<test-name>-output/` | only on normal completion |
| `build-README.md` | Level:TOP task README in target repo (TM mode only) | only when path resolves |

`run-metrics.json` and `run-summary.md` are written by the orchestrator only
when the pipeline exits normally. A stalled or interrupted run produces only
`execution.log`.

`build-README.md` contains the `## Execution Log` table written live during
the run. The walk-up resolution depends on `current-job.txt` pointing into a
still-intact target repo.

### When `last_run/` is not populated

- No previous run exists (first reset after a fresh clone).
- The output dir contains no `execution.log` (e.g. the run was never started).

### Comparing runs

Use `last_run/run-metrics.json` for token and timing comparisons against a
baseline. If the previous run was a stalled-and-resumed pair, see §8 on
execution log merging.

---

## 4. Spec Review Checklist

The spec is the job document written into the PIPELINE-SUBTASK README by
`reset.sh`. **The Oracle must review the spec before running the pipeline.**
A bad spec produces a wasted run — the pipeline will implement exactly what
is written, not what was intended.

Before running the pipeline, confirm:

- [ ] The architecture name matches the actual structure described
      (e.g. "networked monolith" means one binary, one process — not two
      separate services)
- [ ] Every required endpoint is explicitly listed (path, method, status codes)
- [ ] Every parameter model is specified (request body field names and types,
      response field names and types) — do not leave field names ambiguous
- [ ] Language, port(s), storage requirements are unambiguous
- [ ] Binary structure is explicit: how many entry points (`main` packages)?
      For a networked monolith: one binary, multiple listeners. For
      microservices: one binary per service.
- [ ] Testing requirements are stated: unit tests, integration tests, e2e
      acceptance tests — at which levels?
- [ ] The spec has been read end-to-end by the Oracle before submission

---

## 5. Gold Tests

### Why gold/ is separate

The pipeline's TESTER agent writes its own tests derived from the Acceptance
Criteria in the job doc. Gold tests are written by the Oracle and live in
`gold/` — the pipeline agents never see them. This separation ensures:

- The TESTER's tests verify the agent's own understanding of the spec
- The gold tests independently verify the assembled output against the
  original Oracle intent
- Gold test failures reveal spec drift that the TESTER missed

### Structure

Gold tests use the build tag `regression` so they never run during normal
`go test ./...`:

```go
//go:build regression

package gold_test
```

`TestMain` is responsible for:
1. Finding the generated binary (walk output dir for `package main`)
2. Building it
3. Starting it
4. Waiting for all required ports/endpoints to be ready (use a timeout loop)
5. Running all tests
6. Killing the process on exit

### Binary count assertion

The gold test must assert the correct number of `main` packages:

- **Networked monolith**: assert exactly 1 main package. Fail if > 1.
- **Microservices**: assert exactly N main packages (one per service).

This catches architectural drift — if the IMPLEMENTOR produces two binaries
for a monolith, the gold test fails immediately with a clear message.

### Resilience

Gold tests should be tolerant of minor naming variations (e.g. `id` vs `ID`
vs `userId`) while remaining strict about field presence and correctness.
Use a helper like `extractField(m, "id", "ID", "userId")` rather than
hard-coding a single key.

### Running

```bash
cd tests/regression/<test-name>/gold && go test -tags regression -v ./...
```

---

## 6. README Requirements

Every regression test README must include:

- **What this tests** — which pipeline capability (decomposition depth,
  tree traversal, specific routing, etc.)
- **Target system description** — ASCII architecture diagram showing the
  intended component hierarchy and how the pipeline tree maps to it
- **Run order** — step 1 (reset), step 2 (pipeline command), step 3 (gold test)
- **Service specification** — full API contract (endpoints, methods, fields)
- **Expected pipeline routing** — the sequence of `OUTCOME` values expected

---

## 7. Full Run Order

```bash
# Step 1 — Reset to initial state (saves previous run to last_run/)
tests/regression/<test-name>/reset.sh

# Step 2 — Run the pipeline
python3 ai-builder/orchestrator/orchestrator.py \
    --target-repo sandbox/<test-name>-target \
    --output-dir  sandbox/<test-name>-output \
    --epic        main

# Step 3 — Run gold tests
cd tests/regression/<test-name>/gold && go test -tags regression -v ./...
```

Always run reset.sh before each pipeline run. The pipeline is not idempotent —
running it twice without a reset will fail or produce incorrect results.

---

## 8. Resuming a Stalled Run

If the pipeline halts mid-run (rate limit, agent error, process kill), the
task tree and output dir are still intact. Do **not** run `reset.sh` — that
would wipe the in-progress work. Instead, re-run the orchestrator with
`--resume` (or `--clean-resume` — see below):

```bash
python3 ai-builder/orchestrator/orchestrator.py \
    --target-repo sandbox/<test-name>-target \
    --output-dir  sandbox/<test-name>-output \
    --epic        main \
    --resume
```

`--resume` skips the TM mode validation check that requires the initial job
document to be a Level:TOP pipeline-subtask. This check is correct for fresh
runs but wrong for resumes, where `current-job.txt` points to whatever
internal node was active when the pipeline stalled.

### Stale output and `--clean-resume`

If the pipeline stalled during ARCHITECT or IMPLEMENTOR, the output directory
may contain partial or incorrect output from the interrupted component. The
IMPLEMENTOR will read these stale files on the next run, spending tokens
analysing and rewriting wrong code. Use `--clean-resume` instead of
`--resume` to delete them automatically:

```bash
python3 ai-builder/orchestrator/orchestrator.py \
    --target-repo sandbox/<test-name>-target \
    --output-dir  sandbox/<test-name>-output \
    --epic        main \
    --clean-resume
```

`--clean-resume` implies `--resume`. Before starting, it reads the last
role from `execution.log` and applies these rules:

| Stalled role | Action |
|--------------|--------|
| `ARCHITECT` or `IMPLEMENTOR` | Delete OUTPUT_DIR items newer than the last `LEAF_COMPLETE_HANDLER` timestamp. If no LCH has ever run, delete all unprotected items. |
| `TESTER` | Leave output intact — the code was complete; deleting it would waste tokens rebuilding it. |

Protected names are never deleted: `runs/`, `current-job.txt`,
`execution.log`, `run-metrics.json`, `run-summary.md`.

### Execution log behavior on resume

The orchestrator is stateless — each invocation starts a fresh `RunData`.
The resumed run does not inherit the stalled run's invocation records.

| Artifact | Stalled run | Resumed run |
|----------|-------------|-------------|
| `execution.log` | entries appended up to failure | new entries appended after (both present, no separator) |
| Level:TOP README `## Execution Log` table | partial invocations | **overwritten** with only the resumed run's invocations |
| `run-metrics.json` | not written | written on normal completion of the resumed portion |
| `run-summary.md` | not written | written on normal completion of the resumed portion |

If you need to preserve the stalled run's execution log table before resuming,
copy the Level:TOP README manually before re-running:

```bash
cp sandbox/<test-name>-target/project/tasks/main/in-progress/.../build-1/README.md \
   sandbox/<test-name>-output/stalled-run-build-README.md
```

### Merging stalled and resumed execution logs

`execution.log` is append-only and contains entries from both runs
concatenated. Each orchestrator session begins with a `=== Orchestrator:
starting ===` line, so run boundaries are identifiable by timestamp.

The structured `run-metrics.json` only reflects the resumed portion. A merged
JSON covering both runs is not produced automatically. Manual reconstruction
is possible by parsing `execution.log`, but no tooling exists for this yet.

---

## 9. Existing Tests Reference

| Test | Pipeline capability exercised |
|------|-------------------------------|
| `fibonacci/` | Flat atomic — single ARCHITECT→IMPLEMENTOR→TESTER pass |
| `template-setup/` | Task system setup and CLAUDE.md installation |
| `user-service/` | Single-level decomposition — service decomposed into 3 components |
| `platform-monolith/` | Multi-level decomposition — 3-level tree, tree traversal, networked monolith |
