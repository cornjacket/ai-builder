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

The ARCHITECT sets this field. DECOMPOSE_HANDLER reads it deterministically to
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
DECOMPOSE_HANDLER creates one subtask per component
        |
        +--> for each component:
              Oracle prepares job doc
                     |
                     v
              ARCHITECT (design pass)
                     |
                     +--> atomic?   → fills Design + Acceptance Criteria
                     |              → [DOCUMENTER] → IMPLEMENTOR → [DOCUMENTER]
                     |              → TESTER → [DOCUMENTER] → LEAF_COMPLETE_HANDLER marks complete
                     |
                     +--> composite? → outputs sub-components
                                     → [DOCUMENTER] → DECOMPOSE_HANDLER creates sub-subtasks
                                     → recurse
```

---

## ARCHITECT Component List Format

For DECOMPOSE_HANDLER to create subtasks mechanically, the ARCHITECT must write
its component list in a defined format:

```markdown
## Components

| Name | Complexity | Description |
|------|------------|-------------|
| auth-handler | atomic | JWT validation, token issuance, single endpoint |
| user-store   | atomic | CRUD operations on users table, PostgreSQL |
| api-layer    | composite | HTTP routing, middleware — needs further decomposition |
```

DECOMPOSE_HANDLER reads this table and creates one subtask per row using
`new-task.sh`. `Complexity: composite` triggers another decomposition pass.
`Complexity: atomic` proceeds to a design pass (ARCHITECT fills Design +
Acceptance Criteria).

---

## Job Document Per Phase

The job document at every level is the task README, pointed to by
`current-job.txt`. ARCHITECT mode is determined by the `Complexity` field
in the task metadata and the sections present:

| Complexity field | ARCHITECT mode | Sections filled |
|-----------------|----------------|-----------------|
| `—` or `composite` | Decompose | `## Components`, `## Suggested Tools` |
| `atomic` | Design | `## Design`, `## Acceptance Criteria`, `## Suggested Tools` |

DECOMPOSE_HANDLER fills `Complexity`, `Goal`, and `Context` when creating component subtasks.
ARCHITECT fills the remaining sections in place.

---

## Tree Navigation

The two handlers navigate the task tree:

1. ARCHITECT sets `Complexity` field; DECOMPOSE_HANDLER reads it to decide next action
2. If `Complexity: composite` → ARCHITECT decomposes → DECOMPOSE_HANDLER creates subtasks → recurse
3. If `Complexity: atomic` → ARCHITECT designs → IMPLEMENTOR implements → TESTER verifies
4. LEAF_COMPLETE_HANDLER marks task complete, walks up the tree with `on-task-complete.sh`
5. When all siblings are complete, parent is marked complete automatically
6. When the top-level build node completes → `HANDLER_ALL_DONE`

---

## ARCHITECT Outcomes for Decomposition

| Outcome | Meaning |
|---------|---------|
| `ARCHITECT_DECOMPOSITION_READY` | Component list written; DECOMPOSE_HANDLER creates subtasks |
| `ARCHITECT_DESIGN_READY` | Design + Acceptance Criteria complete; ready for IMPLEMENTOR |
| `ARCHITECT_NEEDS_REVISION` | Plan has gaps; ARCHITECT iterates before task creation |
| `ARCHITECT_NEED_HELP` | Halts pipeline; human intervention required |

---

## Deterministic vs. Non-Deterministic Elements

**Deterministic (scriptable):**
- Task directory and file structure
- Handler script invocations (new-task.sh, complete-task.sh, set-current-job.sh)
- Routing table lookup
- Loop termination (all subtasks in complete/ → `HANDLER_ALL_DONE`)
- Template selection (DECOMPOSE_HANDLER reads Complexity field)

**Must be structured for determinism** (AI produces, format is fixed):
- ARCHITECT component list — defined table format so DECOMPOSE_HANDLER can parse mechanically
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

Content required per role per phase:

| Role | Phase | Content required |
|------|-------|-----------------|
| ARCHITECT | Decompose | Data flow description + component table (`## Components`) |
| ARCHITECT | Design | Interface contracts + data structures + dependencies (`## Design`, `## Acceptance Criteria`) |
| IMPLEMENTOR | — | Implementation of the Design section |
| TESTER | — | Acceptance test cases verified against `## Acceptance Criteria` |
