# How to Write a Regression Test

Regression tests verify that the ai-builder **pipeline** behaves correctly —
not just that the generated code works. Each test exercises a specific pipeline
capability (flat atomic, single-level decomposition, multi-level decomposition,
tree traversal, etc.) and uses gold tests to independently confirm the output
matches the original spec.

---

## 1. Purpose

A regression test has two goals:

1. **Pipeline correctness** — the pipeline routes correctly, the TM creates
   the right task structure, agents hand off cleanly, and `TM_ALL_DONE` fires
   at the right time.

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
    gold/
        go.mod        # or equivalent
        gold_test.go  # behavioural gold tests (build tag: regression)
    README.md         # test documentation, architecture diagram, run instructions
```

No other committed files. All generated output goes to `sandbox/` (see §4).

---

## 3. reset.sh Contract

Every `reset.sh` must perform these steps in order:

1. **Wipe and recreate** the target repo at `sandbox/<test-name>-target/`.
2. **Install the task system** using `target/setup-project.sh` and
   `target/init-claude-md.sh`.
3. **Create a USER-TASK** (Oracle-owned pipeline boundary) in `in-progress/`
   using `new-user-task.sh`. This is the human-owned node the pipeline must
   not traverse above.
4. **Create a PIPELINE-SUBTASK** entry point under the USER-TASK using
   `new-pipeline-subtask.sh --level TOP`. This is where the pipeline starts.
5. **Write the spec** into the PIPELINE-SUBTASK's README (overwrite the
   generated template). Complexity must be left as `—` to trigger ARCHITECT
   decompose mode.
6. **Point `current-job.txt`** at the PIPELINE-SUBTASK README using
   `set-current-job.sh --output-dir <sandbox-output-dir>`.
7. **Clear previous output** — remove `execution.log` and `logs/` from the
   output dir.

Print the pipeline run command and gold test command at the end.

### Sandbox paths

| Directory | Purpose |
|-----------|---------|
| `sandbox/<test-name>-target/` | Fresh target repo (task system + generated code) |
| `sandbox/<test-name>-output/` | Pipeline output dir (execution.log, logs/, current-job.txt) |

**Never use `/tmp/`** for target repos or output dirs. Sandbox paths are
tracked in git (gitignored content, committed structure) and survive sessions.

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
# Step 1 — Reset to initial state
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

## 8. Existing Tests Reference

| Test | Pipeline capability exercised |
|------|-------------------------------|
| `fibonacci/` | Flat atomic — single ARCHITECT→IMPLEMENTOR→TESTER pass |
| `template-setup/` | Task system setup and CLAUDE.md installation |
| `user-service/` | Single-level decomposition — service decomposed into 3 components |
| `platform-monolith/` | Multi-level decomposition — 3-level tree, tree traversal, networked monolith |
