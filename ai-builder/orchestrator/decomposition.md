# Multi-Level Decomposition

The pipeline handles a single scoped job per run. Decomposition is the
mechanism that produces those jobs from a high-level request. A complex
service cannot go directly to IMPLEMENTOR — it must be broken into
implementable components first, potentially across multiple levels.

---

## The Problem

A high-level request ("build an auth service") produces a component tree,
not a flat list. Some components are atomic (implementable directly) and
some are composite (need further decomposition before implementation).

```
auth-service
    ├── auth-handler          (atomic → implement)
    ├── api-layer             (composite → decompose further)
    │     ├── router          (atomic → implement)
    │     ├── middleware      (atomic → implement)
    │     └── rate-limiter    (composite → decompose further)
    │           ├── counter   (atomic → implement)
    │           └── store     (atomic → implement)
    └── user-store            (atomic → implement)
```

The task system already supports arbitrary nesting — task directories nest
to any depth. Decomposition populates this structure; the N-phase pipeline
runs only on leaf (atomic) nodes.

---

## The `Complexity` Field

Every task/subtask README carries a `Complexity` field:

```markdown
| Complexity | atomic |
```

or

```markdown
| Complexity | composite |
```

- `atomic` — implementable as a single ARCHITECT→IMPLEMENTOR→TESTER run
- `composite` — requires a decomposition pass before implementation

The ARCHITECT sets this field. TASK_MANAGER reads it deterministically to
decide next action — no AI re-derivation at routing time.

---

## Decomposition as a Sub-Loop

```
[High-level task]
        |
        v
Oracle prepares job doc (decompose mode)
        |
        v
ARCHITECT (decompose pass)
        |
        v
  Structured component list (see format below)
        |
        v
[DOCUMENTER hook] → writes non-leaf README for this directory
        |
        v
TASK_MANAGER creates one subtask per component
        |
        +--> for each component:
              Oracle prepares job doc
                     |
                     v
              ARCHITECT (design pass)
                     |
                     +--> atomic?   → fills Design + Acceptance Criteria
                     |              → [DOCUMENTER] → IMPLEMENTOR → [DOCUMENTER]
                     |              → TESTER → [DOCUMENTER] → TM marks complete
                     |
                     +--> composite? → outputs sub-components
                                     → [DOCUMENTER] → TM creates sub-subtasks
                                     → recurse
```

---

## ARCHITECT Component List Format

For TASK_MANAGER to create subtasks mechanically, the ARCHITECT must write
its component list in a defined format:

```markdown
## Components

| Name | Complexity | Description |
|------|------------|-------------|
| auth-handler | atomic | JWT validation, token issuance, single endpoint |
| user-store   | atomic | CRUD operations on users table, PostgreSQL |
| api-layer    | composite | HTTP routing, middleware — needs further decomposition |
```

TASK_MANAGER reads this table and creates one subtask per row using
`new-task.sh`. `Complexity: composite` triggers another decomposition pass.
`Complexity: atomic` proceeds to a design pass (ARCHITECT fills Design +
Acceptance Criteria).

---

## Job Templates Per Phase

Different phases use different job document shapes. The template signals
to the ARCHITECT what mode it is in:

| Template | ARCHITECT mode | Output |
|----------|---------------|--------|
| `JOB-service-build` | Decompose | Structured component list |
| `JOB-component-design` | Design | Design + Acceptance Criteria for one component |

TASK_MANAGER selects the template when creating each job. The template
constrains the ARCHITECT's output format.

---

## Tree Navigation

TASK_MANAGER navigates the task tree top-down:

1. Find the next incomplete node using `list-tasks.sh`
2. If `Complexity: composite` → run decomposition pass (ARCHITECT → TM creates subtasks)
3. If `Complexity: atomic` → run design + implementation pass
4. Mark complete with `complete-task.sh`
5. Move up the tree; when all siblings complete, parent is complete
6. When all nodes complete → `ALL_DONE`

---

## ARCHITECT Outcomes for Decomposition

| Outcome | Meaning |
|---------|---------|
| `COMPONENTS_READY` | Component list written; TASK_MANAGER should create subtasks |
| `COMPONENT_READY` | Design + Acceptance Criteria complete; ready for IMPLEMENTOR |
| `DONE` | Used in implementation pass (existing) |
| `NEEDS_REVISION` | Plan has gaps; iterate before task creation |

These outcomes are not yet implemented in the orchestrator. See task
`8eea17-implement-decomposition-in-orchestrator`.

---

## Deterministic vs. Non-Deterministic Elements

**Deterministic (scriptable):**
- Task directory and file structure
- TASK_MANAGER script invocations (new-task.sh, move-task.sh, complete-task.sh)
- Routing table lookup
- Loop termination (all subtasks in complete/ → `ALL_DONE`)
- Template selection (TASK_MANAGER reads Complexity field)

**Must be structured for determinism** (AI produces, format is fixed):
- ARCHITECT component list — defined table format so TASK_MANAGER can parse
  without AI interpretation
- `Complexity` field — explicit `atomic` or `composite`, not prose

**Genuinely non-deterministic** (accept and design around):
- Component boundary decisions
- Design and acceptance criteria content
- Whether implementation is correct (caught by TESTER)

---

## README Content by Level

The README hierarchy mirrors the decomposition tree exactly. Each level of
decomposition produces a README for that directory — the ARCHITECT is the
content producer, DOCUMENTER formats and owns the file.

**Non-leaf README** (produced by ARCHITECT decompose pass):

```
## <service-name>

One sentence: what does this part of the system do?

## Data Flow

    client → [api-layer] → [auth-handler] → [user-store]
                  |               |
                  v               v
             rate-limit      JWT issue/validate

## Components

| Component    | Responsibility                        |
|--------------|---------------------------------------|
| api-layer    | HTTP routing, middleware, rate-limit  |
| auth-handler | JWT validation and token issuance     |
| user-store   | User CRUD, PostgreSQL                 |
```

Bounded by design — only describes this level's scope. No implementation
detail. Links down to child READMEs.

**Leaf README** (skeleton by ARCHITECT design pass, completed by IMPLEMENTOR):
- Purpose and interface contracts (inputs, outputs, error conditions)
- Data structures and types
- Dependencies (what this component calls, what calls it)
- Usage examples
- Implementation notes (non-obvious decisions, known limitations)

Bulk of technical detail lives here. Non-leaf documents link down to it.

---

## Pipeline Documentation Responsibilities

Content producers write *what* the system does. DOCUMENTER writes *the document*.

| Role | Produces |
|------|----------|
| ARCHITECT (decompose pass) | Data flow description, component table with responsibilities |
| ARCHITECT (design pass) | Interface contracts, data structures, dependencies |
| IMPLEMENTOR | Implementation notes, usage examples, known limitations |
| TESTER | Acceptance test cases, documented alongside test files |
| **DOCUMENTER** | **All README files — formats, organises, and maintains** |

Each job template specifies what content the producing role must provide:

| Template | Role | Content required |
|----------|------|-----------------|
| `JOB-service-build` | ARCHITECT | Data flow description + component list with responsibilities |
| `JOB-component-design` | ARCHITECT | Interface contracts + data structures + dependencies |
| `JOB-component-implement` | IMPLEMENTOR | Implementation notes + usage examples + known limitations |
| `JOB-component-test` | TESTER | Acceptance test cases documented alongside test files |
