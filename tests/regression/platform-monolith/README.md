# Regression Test: Platform Monolith (Multi-Level Decomposition)

This test verifies that the pipeline correctly handles a multi-level decomposition
tree: a top-level platform that decomposes into two services, where one service
(IAM) itself decomposes into two internal components. The pipeline must traverse
all levels, implementing and testing each before walking up to integrate the next.

---

## Target System

A networked monolith platform in Go. One binary (`cmd/platform/main.go`),
one process, two HTTP listeners on separate ports.

```
platform binary  (single process)
│
├── metrics listener    port 8081
│   Accepts frontend user interaction events (click-mouse, submit-form).
│   POST /events, GET /events
│
└── iam listener        port 8082
    Identity and access management. Two internal components:
    │
    ├── auth-lifecycle
    │   User registration, lookup, deletion. Login/logout with token issuance.
    │   POST /users, GET /users/{id}, DELETE /users/{id}
    │   POST /auth/login, POST /auth/logout
    │
    └── authz-rbac
        Role management and permission checks.
        POST /roles, GET /roles
        POST /users/{id}/roles, GET /users/{id}/roles
        POST /authz/check
```

---

## Intended Task Hierarchy

The ARCHITECT will produce this decomposition tree. Actual component names and
boundaries are decided by the pipeline — the structure below shows the intended
shape and the Level field at each integrate step.

```
platform  [USER-TASK, pipeline boundary]
└── build-1  [PIPELINE-SUBTASK, Level=TOP]
    │
    ├── metrics-ingestion-service  [composite, INTERNAL]
    │   ├── <atomic components>    [decided by ARCHITECT]
    │   └── integrate              [INTERNAL] — wires metrics service, port 8081
    │                                           contract tests only
    │
    ├── iam-service                [composite, INTERNAL]
    │   ├── auth-lifecycle         [composite, INTERNAL]
    │   │   ├── <atomic components>
    │   │   └── integrate          [INTERNAL] — wires auth-lifecycle components
    │   │                                       contract tests only
    │   ├── authz-rbac             [composite, INTERNAL]
    │   │   ├── <atomic components>
    │   │   └── integrate          [INTERNAL] — wires authz-rbac components
    │   │                                       contract tests only
    │   └── integrate              [INTERNAL] — wires auth-lifecycle + authz-rbac
    │                                           full IAM API tests on port 8082
    │
    └── integrate                  [TOP]       — e2e tests across both services
                                               both ports running simultaneously
```

**Level semantics:**
- `INTERNAL` integrate: verifies this level's contract (component interface tests)
- `TOP` integrate: full end-to-end acceptance tests with both services running

---

## What This Tests

The full multi-level decomposition and tree traversal pipeline:

1. **ARCHITECT** (decompose: build-1) → produces Components table for platform
2. **DECOMPOSE_HANDLER** → creates metrics, iam, integrate(TOP) subtasks
3. **ARCHITECT** (decompose: iam) → produces sub-components
4. **DECOMPOSE_HANDLER** → creates atomic sub-components + integrate(INTERNAL)
5. Each atomic component: **ARCHITECT** (design) → **IMPLEMENTOR** → **TESTER** → **LEAF_COMPLETE_HANDLER** advances
6. iam integrate(INTERNAL): **ARCHITECT** → **IMPLEMENTOR** → **TESTER** → **LEAF_COMPLETE_HANDLER** walks up
7. build-1 integrate(TOP): **ARCHITECT** → **IMPLEMENTOR** → **TESTER** → **LEAF_COMPLETE_HANDLER** signals `HANDLER_ALL_DONE`

---

## Directory Structure

```
platform-monolith/
    gold/
        go.mod
        gold_test.go          # e2e gold tests against both running services
    reset.sh                  # sets up fresh target repo in sandbox/
    README.md                 # this file
```

---

## Run Order

**Step 1 — Reset:**

```bash
tests/regression/platform-monolith/reset.sh
```

Creates a fresh target repo at `sandbox/platform-monolith-target/`, installs
the task system, creates the `platform` USER-TASK and the `build-1`
PIPELINE-SUBTASK (Level=TOP) under it, and writes `current-job.txt`.

**Step 2 — Run the pipeline** (from repo root):

```bash
python3 ai-builder/orchestrator/orchestrator.py \
    --target-repo sandbox/platform-monolith-target \
    --output-dir  sandbox/platform-monolith-output \
    --epic        main
```

**Step 3 — Run the gold test:**

```bash
cd tests/regression/platform-monolith/gold && go test -tags regression ./...
```

---

## Service Specification

### Metrics Ingestion Service — port 8081

Language: Go. Storage: in-memory.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/events` | POST | Record event; body: `{"type": "click-mouse"\|"submit-form", "userId": "<str>", "payload": {}}` |
| `/events` | GET  | List all recorded events |

### IAM Service — port 8082

Language: Go. Storage: in-memory.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/users` | POST | Register user; body: `{"username": "<str>", "password": "<str>"}` |
| `/users/{id}` | GET | Get user by ID |
| `/users/{id}` | DELETE | Delete user |
| `/auth/login` | POST | Authenticate; body: `{"username": "<str>", "password": "<str>"}` → token |
| `/auth/logout` | POST | Invalidate token; header: `Authorization: Bearer <token>` |
| `/roles` | POST | Create role; body: `{"name": "<str>", "permissions": ["<str>"]}` |
| `/roles` | GET | List all roles |
| `/users/{id}/roles` | POST | Assign role to user; body: `{"roleId": "<str>"}` |
| `/users/{id}/roles` | GET | Get user's roles |
| `/authz/check` | POST | Check permission; body: `{"userId": "<str>", "permission": "<str>"}` → `{"allowed": bool}` |

---

## Expected Pipeline Routing

```
ARCHITECT (decompose: build-1)              → ARCHITECT_DECOMPOSITION_READY → DECOMPOSE_HANDLER
DECOMPOSE_HANDLER (create build-1 subtasks) → HANDLER_SUBTASKS_READY        → ARCHITECT

ARCHITECT (decompose: iam)                  → ARCHITECT_DECOMPOSITION_READY → DECOMPOSE_HANDLER
DECOMPOSE_HANDLER (create iam subtasks)     → HANDLER_SUBTASKS_READY        → ARCHITECT
  ARCHITECT (design: auth-lifecycle)        → ARCHITECT_DESIGN_READY        → IMPLEMENTOR
  IMPLEMENTOR / TESTER (auth-lifecycle)     → TESTER_TESTS_PASS             → LEAF_COMPLETE_HANDLER
  LEAF_COMPLETE_HANDLER (advance)           → HANDLER_SUBTASKS_READY        → ARCHITECT
  ARCHITECT (design: authz-rbac)            → ARCHITECT_DESIGN_READY        → IMPLEMENTOR
  IMPLEMENTOR / TESTER (authz-rbac)         → TESTER_TESTS_PASS             → LEAF_COMPLETE_HANDLER
  LEAF_COMPLETE_HANDLER (advance)           → HANDLER_SUBTASKS_READY        → ARCHITECT
  ARCHITECT (design: iam/integrate)         → ARCHITECT_DESIGN_READY        → IMPLEMENTOR
  TESTER (iam integrate, INTERNAL)          → TESTER_TESTS_PASS             → LEAF_COMPLETE_HANDLER
  LEAF_COMPLETE_HANDLER (walk up)           → HANDLER_SUBTASKS_READY        → ARCHITECT

ARCHITECT (design: metrics)                 → ARCHITECT_DESIGN_READY        → IMPLEMENTOR
IMPLEMENTOR / TESTER (metrics)              → TESTER_TESTS_PASS             → LEAF_COMPLETE_HANDLER
LEAF_COMPLETE_HANDLER (advance)             → HANDLER_SUBTASKS_READY        → ARCHITECT

ARCHITECT (design: build-1 integrate, TOP)  → ARCHITECT_DESIGN_READY        → IMPLEMENTOR
IMPLEMENTOR                                 → IMPLEMENTOR_IMPLEMENTATION_DONE → TESTER
TESTER (e2e: both services)                 → TESTER_TESTS_PASS             → LEAF_COMPLETE_HANDLER
LEAF_COMPLETE_HANDLER (DONE)                → HANDLER_ALL_DONE              → (halt)
```
