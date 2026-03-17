# Pipeline Behavior

End-to-end description of how the ai-builder pipeline processes work: from a
top-level task through decomposition, implementation, and tree traversal back
to completion.

---

## Pipeline Modes

The pipeline operates in three structural modes depending on task complexity.

### Flat Atomic

The simplest case. A single task is directly implementable.

```
Oracle sets current-job.txt → ARCHITECT (design) → IMPLEMENTOR → TESTER → done
```

### Single-Level Decomposition

A service is decomposed into components, each implemented in sequence.

```
ARCHITECT (decompose)
    → DECOMPOSE_HANDLER creates component subtasks
    → for each component:
        ARCHITECT (design) → IMPLEMENTOR → TESTER
        → LEAF_COMPLETE_HANDLER advances to next component
    → last component done → HANDLER_ALL_DONE
```

### Multi-Level Decomposition

A composite component is itself decomposed further. The tree can nest to
any depth. The pipeline navigates this tree without the orchestrator knowing
the structure — all navigation is handled by `on-task-complete.sh` and the
handler prompts.

```
ARCHITECT (decompose: service)
    → DECOMPOSE_HANDLER creates [component-A, component-B, integrate]
    → component-A: ARCHITECT (decompose: component-A)
        → DECOMPOSE_HANDLER creates [sub-1, sub-2, integrate-A]
        → sub-1: ARCHITECT (design) → IMPLEMENTOR → TESTER → LEAF_COMPLETE_HANDLER advances
        → sub-2: ARCHITECT (design) → IMPLEMENTOR → TESTER → LEAF_COMPLETE_HANDLER advances
        → integrate-A: ARCHITECT (design) → IMPLEMENTOR → TESTER
            → on-task-complete: last at this level → walk up
            → LEAF_COMPLETE_HANDLER advances to component-B
    → component-B: ARCHITECT (design) → IMPLEMENTOR → TESTER → LEAF_COMPLETE_HANDLER advances
    → integrate: ARCHITECT (design) → IMPLEMENTOR → TESTER
        → on-task-complete: last at service level, parent is USER-TASK → DONE
```

---

## The Level Field

Every pipeline-subtask README has a `Level` field in its metadata table.

| Value | Meaning |
|-------|---------|
| `TOP` | Top-level entry point. The integrate step should produce a runnable, end-to-end testable unit. |
| `INTERNAL` | Internal component. The integrate step wires components to satisfy this level's contract, but the result is not independently runnable. |

### Who Sets It

- **Oracle** sets `Level: TOP` on `build-N` entry-point tasks by passing
  `--level TOP` to `new-pipeline-subtask.sh`.
- **TM** creates all component subtasks with the default `Level: INTERNAL`.
- **TM** sets the integration component's Level to match its parent's Level
  (inherited). This ensures that at a TOP-level service, the final integrate
  step knows it must produce a runnable, end-to-end testable result.

### What It Controls

The ARCHITECT reads the Level field when handling an `integrate` component:

- `Level: TOP` → write end-to-end acceptance tests, verify the service is
  runnable and the full use-case works.
- `Level: INTERNAL` → write contract tests only (interface, not deployment).
  The component will be tested end-to-end when its parent's integrate runs.

---

## Decompose Mode Trigger

ARCHITECT mode is determined by the `Complexity` field in the task README:

| Complexity field | ARCHITECT mode |
|-----------------|----------------|
| `—` (unset) or `composite` | Decompose: produce Components table |
| `atomic` | Design: fill Design + Acceptance Criteria sections |

The orchestrator reads this field and sets `valid_outcomes` accordingly
before invoking the ARCHITECT. No AI interpretation at routing time.

---

## Tree Traversal Algorithm

After a leaf task completes (TESTER passes), `LEAF_COMPLETE_HANDLER` calls `on-task-complete.sh`.
This script encapsulates three operations:

1. **`complete-task.sh`** — marks the leaf `[x]` in its parent's subtask list.
2. **`check-stop-after.sh`** — returns `STOP_AFTER` if the task has
   `Stop-after: true`, signalling that Oracle review is required.
3. **`advance-pipeline.sh`** — upward tree traversal.

### advance-pipeline.sh Loop

```
current = completed leaf README

loop:
  last_task = read Last-task field from current

  if last_task != "true":
    # More siblings at this level — find the next incomplete one.
    next = next-subtask.sh --parent <parent>
    set-current-job.sh → next
    return "NEXT <next>"

  # Current was the last at this level — walk up.
  parent_readme = dirname(dirname(current))/README.md

  if parent is human-owned (Task-type: USER-TASK or USER-SUBTASK):
    # Pipeline boundary reached — cannot mark human task complete.
    return "DONE"

  # Mark the composite parent complete and continue upward.
  complete-task.sh --parent <grandparent> --name <parent>

  if grandparent is human-owned:
    return "DONE"

  # Walk up: check if the parent was also the last at its level.
  current = parent_readme
  continue
```

### Human/Pipeline Boundary Detection

The traversal stops when it reaches a node whose `Task-type` is `USER-TASK`
or `USER-SUBTASK`. These are human-owned nodes — the pipeline must not mark
them complete or traverse above them. This is the mechanism by which the
pipeline stays contained within the subtree the Oracle submitted.

`USER-TASK` and `USER-SUBTASK` nodes are never created by the pipeline.
They are created by the Oracle (human operator) and serve as the root
boundary of any pipeline run.

### The Last-task Field

The `Last-task` field on each pipeline-subtask is set at task creation time:

- The integration component gets `Last-task: true`.
- All other components get `Last-task: false`.

This embeds traversal intent into the task itself, avoiding the need to
inspect sibling state at runtime.

---

## on-task-complete.sh Return Values

| Return | Handler outcome |
|--------|-----------------|
| `NEXT <path>` | More subtasks remain. `current-job.txt` updated. → `HANDLER_SUBTASKS_READY` |
| `DONE` | All subtasks in this pipeline tree complete. → `HANDLER_ALL_DONE` |
| `STOP_AFTER` | `Stop-after: true` on completed task. Human review required. → `HANDLER_STOP_AFTER` |

---

## Stop-after

Any pipeline-subtask can request a pause after completion by setting
`Stop-after: true` in its metadata. This is typically set by the Oracle
on a specific `build-N` task to inspect results before the pipeline continues.

When `on-task-complete.sh` detects `Stop-after: true`, it returns `STOP_AFTER`
before running tree traversal. `LEAF_COMPLETE_HANDLER` emits `HANDLER_STOP_AFTER`,
the orchestrator halts with exit 0, and Oracle must resume manually.

---

## Two-Level Decomposition: Routing Diagram

```
Oracle: current-job.txt → auth-service (TOP, Complexity: —)

ARCHITECT ─────────────────────────── decompose
  outcome: ARCHITECT_DECOMPOSITION_READY
      │
      ▼
DECOMPOSE_HANDLER ─────────────────── create subtasks
  creates: [auth-handler(atomic), user-store(atomic), integrate(TOP,Last-task:true)]
  current-job.txt → auth-handler
  outcome: HANDLER_SUBTASKS_READY
      │
      ▼
ARCHITECT ─────────────────────────── design auth-handler (atomic)
  outcome: ARCHITECT_DESIGN_READY
      │
IMPLEMENTOR → TESTER ─────────────── TESTER_TESTS_PASS
      │
      ▼
LEAF_COMPLETE_HANDLER ─────────────── on-task-complete(auth-handler)
  → complete auth-handler [x]
  → Last-task=false → NEXT user-store
  current-job.txt → user-store
  outcome: HANDLER_SUBTASKS_READY
      │
      ▼
ARCHITECT → IMPLEMENTOR → TESTER ─── TESTER_TESTS_PASS (user-store)
      │
      ▼
LEAF_COMPLETE_HANDLER ─────────────── on-task-complete(user-store)
  → complete user-store [x]
  → Last-task=false → NEXT integrate
  current-job.txt → integrate
  outcome: HANDLER_SUBTASKS_READY
      │
      ▼
ARCHITECT (integrate, Level=TOP) ─── design with e2e tests
  outcome: ARCHITECT_DESIGN_READY
      │
IMPLEMENTOR → TESTER ─────────────── TESTER_TESTS_PASS (integrate)
      │
      ▼
LEAF_COMPLETE_HANDLER ─────────────── on-task-complete(integrate)
  → complete integrate [x]
  → Last-task=true → walk up
  → parent (auth-service) is USER-TASK → DONE
  outcome: HANDLER_ALL_DONE

Orchestrator halts (exit 0).
```
