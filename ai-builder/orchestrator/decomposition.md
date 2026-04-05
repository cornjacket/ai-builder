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

For DECOMPOSE_HANDLER to create subtasks mechanically, the ARCHITECT emits a
`<components>` block inside its XML `<response>`. Each `<component>` entry
has `name`, `complexity`, `source_dir`, and `description`:

```xml
<response>
  <outcome>ARCHITECT_DECOMPOSITION_READY</outcome>
  <handoff>...</handoff>
  <components>
    <component>
      <name>auth-handler</name>
      <complexity>atomic</complexity>
      <source_dir>internal/auth/handler</source_dir>
      <description>JWT validation, token issuance, POST /auth/login and POST /auth/logout</description>
    </component>
    <component>
      <name>user-store</name>
      <complexity>atomic</complexity>
      <source_dir>internal/auth/store</source_dir>
      <description>CRUD operations on users — in-memory map[string]User guarded by sync.RWMutex</description>
    </component>
    <component>
      <name>integrate-auth</name>
      <complexity>atomic</complexity>
      <source_dir>.</source_dir>
      <description>Wire auth-handler and user-store; return http.Handler for the caller</description>
    </component>
  </components>
</response>
```

DECOMPOSE_HANDLER parses this array and creates one subtask per entry.
`Complexity: composite` triggers another decomposition pass on that subtask.
`Complexity: atomic` proceeds to a design pass. The final entry must always
start with `integrate-` — it wires the sibling components together. The
`integrate-<scope>` naming makes execution logs unambiguous when multiple
integration steps appear in the same run (e.g. `integrate-iam`,
`integrate-platform`).

The `source_dir` field drives output directory placement. The description is
copied verbatim into the component subtask's `goal` field in `task.json` — it
is the only input the design-mode ARCHITECT sees, so it must be a complete contract.

---

## Task State Per Phase

The orchestrator injects fields from `task.json` inline into every agent
prompt. ARCHITECT mode is determined by the `complexity` field:

| `complexity` value | ARCHITECT mode | Produces |
|--------------------|----------------|----------|
| `—` or `composite` | Decompose | XML `<components>` array in `<response>` block |
| `atomic` | Design | XML `<response>` with `design`, `acceptance_criteria`, `test_command`; README.md in output dir |

`task.json` fields written and consumed across phases:

| Field | Written by | Consumed by |
|-------|-----------|-------------|
| `goal` | Oracle / DECOMPOSE_HANDLER | ARCHITECT, IMPLEMENTOR |
| `context` | Oracle / DECOMPOSE_HANDLER | ARCHITECT, IMPLEMENTOR |
| `complexity` | DECOMPOSE_HANDLER | Orchestrator (mode selection) |
| `level` | DECOMPOSE_HANDLER | Orchestrator (scope of integrate step) |
| `output_dir` | DECOMPOSE_HANDLER | Orchestrator (where to write files) |
| `design` | ARCHITECT (stored by orchestrator) | IMPLEMENTOR |
| `acceptance_criteria` | ARCHITECT (stored by orchestrator) | IMPLEMENTOR |
| `test_command` | ARCHITECT (stored by orchestrator) | TESTER |
| `documents_written` | ARCHITECT / IMPLEMENTOR via `<response>` | DOCUMENTER (skip check) |

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
- Handler script invocations (`new-pipeline-subtask.sh`, `complete-task.sh`, `set-current-job.sh`)
- Routing table lookup
- Loop termination (all subtasks complete → `HANDLER_ALL_DONE`)
- Template selection (orchestrator reads `complexity` from `task.json`)

**Must be structured for determinism** (AI produces, format is fixed):
- ARCHITECT component list — XML `<components>` block parsed by orchestrator; passed as array to DECOMPOSE_HANDLER
- `complexity` field in XML response — must be exactly `atomic` or `composite`, not prose

**Genuinely non-deterministic** (accept and design around):
- Component boundary decisions
- Design and acceptance criteria content
- Whether implementation is correct (caught by TESTER)

---

## Output Directory Structure

The output directory tree mirrors the decomposition tree. ARCHITECT writes
documentation directly to the output directory; DECOMPOSE_HANDLER creates
subdirectories keyed by `source_dir`.

**Non-leaf output directory** (ARCHITECT decompose pass writes README.md):

```
# iam

Purpose: Identity and access management service.
Tags: architecture, design

## File Index
...

## Overview
...component wiring, route summary...
```

**Leaf output directory** (ARCHITECT design pass writes README.md +
optional named detail files; IMPLEMENTOR writes source files + companion docs):

```
internal/iam/lifecycle/
  README.md         ← ARCHITECT: Purpose/Tags, file index, overview, API contract
  api.md            ← ARCHITECT: full endpoint spec (if >3 endpoints)
  lifecycle.go      ← IMPLEMENTOR: source with Purpose:/Tags: package comment
  lifecycle_test.go ← IMPLEMENTOR: tests
  lifecycle.md      ← IMPLEMENTOR: companion doc for non-trivial logic
```

---

## Documentation Responsibilities

| Role | Produces |
|------|----------|
| ARCHITECT (decompose pass) | `README.md` in the composite output dir — overview, file index, data flow |
| ARCHITECT (design pass) | `README.md` + optional named detail files (`api.md`, `models.md`, etc.) in the leaf output dir |
| IMPLEMENTOR | Source files + companion `.md` files; mandatory `Purpose:`/`Tags:` package comment in each source file |
| TESTER | Internal — runs test command from `task.json`; no documentation output |
| DOCUMENTER_POST_ARCHITECT / _IMPLEMENTOR | Internal — scans output dir for `.md` files with Purpose:/Tags: headers; rebuilds README index and `master-index.md` |
