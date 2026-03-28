# Regression Test: User Service (Decomposition)

This test verifies that the decomposition pipeline correctly decomposes a
service-level job into atomic components, designs and implements each one,
and produces a working HTTP service.

---

## Directory Structure

```
user-service/
    gold/                               # committed — never visible to pipeline agents
        gold_test.go                    # gold HTTP behavioural tests (build tag: regression)
    work/                               # pipeline output directory
        JOB-user-service.md.template    # committed — pristine job document
        JOB-user-service.md             # gitignored — restored by reset.sh
        current-job.txt                 # gitignored — written by orchestrator (TM mode)
        logs/                           # gitignored — per-role agent logs
        execution.log                   # gitignored — orchestrator run log
    reset.sh                            # resets to initial state; creates /tmp target repo
    README.md                           # this file
```

### Why gold/ and work/ are separate

The pipeline's `--output-dir` is `sandbox/user-service-output/`.
The gold tests run separately after the pipeline completes. The TESTER agent
has no visibility into `gold/`, so it derives its own tests from the
Acceptance Criteria. The gold tests independently verify the assembled binary
behaviour. All regression tests follow this `gold/` / `work/` separation.

---

## What This Tests

The full decomposition pipeline loop:

1. **ARCHITECT** (decompose mode) — reads the task goal/context, produces a
   component array in its XML response (`ARCHITECT_DECOMPOSITION_READY`)
2. **DECOMPOSE_HANDLER** — reads the component table, creates subtasks in the
   target repo's task system, queues the first one (`HANDLER_SUBTASKS_READY`)
3. **ARCHITECT** (design mode) — designs the first component (`ARCHITECT_DESIGN_READY`)
4. **IMPLEMENTOR** — implements the component (`IMPLEMENTOR_IMPLEMENTATION_DONE`)
5. **TESTER** — tests the component (`TESTER_TESTS_PASS`)
6. **LEAF_COMPLETE_HANDLER** — marks task complete, advances to next sibling
7. Steps 3–6 repeat for each component
8. **LEAF_COMPLETE_HANDLER** signals `HANDLER_ALL_DONE` when all components are done

After the pipeline completes, `gold/gold_test.go` verifies the assembled
service's HTTP behaviour end-to-end.

---

## Run Order

**Step 1 — Reset:**

```bash
tests/regression/user-service/reset.sh
```

Creates a fresh target repo at `sandbox/user-service-target/`, installs
the task system, places the `user-service` task in `in-progress/`, and
writes `current-job.txt` (simulating Oracle).

**Step 2 — Run the pipeline** (from repo root):

```bash
python3 ai-builder/orchestrator/orchestrator.py \
    --target-repo   sandbox/user-service-target \
    --output-dir    sandbox/user-service-output \
    --epic          main \
    --state-machine ai-builder/orchestrator/machines/default.json
```

**Step 3 — Run the gold test:**

```bash
cd tests/regression/user-service/gold && go test -tags regression ./...
```

---

## Service Specification

The pipeline is given only this specification — it must not have components
pre-specified. The ARCHITECT decides the decomposition.

- Language: Go
- Port: `8080`
- Routes: `POST /users`, `GET /users/{id}`, `PUT /users/{id}`, `DELETE /users/{id}`
- Response format: JSON
- Storage: in-memory
- No authentication or authorisation

---

## Expected Pipeline Routing

```
ARCHITECT (decompose)      → ARCHITECT_DECOMPOSITION_READY → DECOMPOSE_HANDLER
DECOMPOSE_HANDLER          → HANDLER_SUBTASKS_READY        → ARCHITECT (design, component 1)
ARCHITECT (design)         → ARCHITECT_DESIGN_READY        → IMPLEMENTOR
IMPLEMENTOR                → IMPLEMENTOR_IMPLEMENTATION_DONE → TESTER
TESTER                     → TESTER_TESTS_PASS             → LEAF_COMPLETE_HANDLER
LEAF_COMPLETE_HANDLER      → HANDLER_SUBTASKS_READY        → ARCHITECT (next component)
... (repeat per component)
LEAF_COMPLETE_HANDLER      → HANDLER_ALL_DONE              → (halt)
```
