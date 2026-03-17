# Routing

The orchestrator routes between roles using a lookup table keyed on
`(current_role, outcome)`. Each entry maps to either the next role name
or `None` (halt).

---

## ROUTES Table

### TM Mode

| From | Outcome | To |
|------|---------|----|
| ARCHITECT | `ARCHITECT_DESIGN_READY` | IMPLEMENTOR |
| ARCHITECT | `ARCHITECT_DECOMPOSITION_READY` | DECOMPOSE_HANDLER |
| ARCHITECT | `ARCHITECT_NEEDS_REVISION` | ARCHITECT *(self-loop — iteration limit applies)* |
| ARCHITECT | `ARCHITECT_NEED_HELP` | halt |
| IMPLEMENTOR | `IMPLEMENTOR_IMPLEMENTATION_DONE` | TESTER |
| IMPLEMENTOR | `IMPLEMENTOR_NEEDS_ARCHITECT` | ARCHITECT |
| IMPLEMENTOR | `IMPLEMENTOR_NEED_HELP` | halt |
| TESTER | `TESTER_TESTS_PASS` | LEAF_COMPLETE_HANDLER |
| TESTER | `TESTER_TESTS_FAIL` | IMPLEMENTOR |
| TESTER | `TESTER_NEED_HELP` | halt |
| DECOMPOSE_HANDLER | `HANDLER_SUBTASKS_READY` | ARCHITECT |
| DECOMPOSE_HANDLER | `HANDLER_NEED_HELP` | halt |
| LEAF_COMPLETE_HANDLER | `HANDLER_SUBTASKS_READY` | ARCHITECT |
| LEAF_COMPLETE_HANDLER | `HANDLER_ALL_DONE` | halt |
| LEAF_COMPLETE_HANDLER | `HANDLER_STOP_AFTER` | halt *(Oracle intervention required)* |
| LEAF_COMPLETE_HANDLER | `HANDLER_NEED_HELP` | halt |

### Non-TM Mode

| From | Outcome | To |
|------|---------|----|
| ARCHITECT | `ARCHITECT_DESIGN_READY` | IMPLEMENTOR |
| ARCHITECT | `ARCHITECT_NEED_HELP` | halt |
| IMPLEMENTOR | `IMPLEMENTOR_IMPLEMENTATION_DONE` | TESTER |
| IMPLEMENTOR | `IMPLEMENTOR_NEEDS_ARCHITECT` | ARCHITECT |
| IMPLEMENTOR | `IMPLEMENTOR_NEED_HELP` | halt |
| TESTER | `TESTER_TESTS_PASS` | halt (pipeline complete) |
| TESTER | `TESTER_TESTS_FAIL` | IMPLEMENTOR |
| TESTER | `TESTER_NEED_HELP` | halt |

DOCUMENTER hook does not run in non-TM mode.

---

## Task Completion and Tree Traversal

When TESTER passes for a subtask, `LEAF_COMPLETE_HANDLER` calls `on-task-complete.sh`
with the completed subtask's README. This script handles three operations atomically:

1. Marks the subtask complete (`[x]`) in its parent's subtask list.
2. Checks `Stop-after: true` — if set, returns `STOP_AFTER`.
3. Runs upward tree traversal (`advance-pipeline.sh`):
   - If `Last-task: false` → finds the next sibling → returns `NEXT <path>`
   - If `Last-task: true` → walks up to the parent composite node, marks it
     complete, and continues upward until a sibling is found or the pipeline
     boundary (a human-owned `USER-TASK` or `USER-SUBTASK`) is reached.

| `on-task-complete.sh` output | Handler outcome |
|-----------------------------|-----------------|
| `NEXT <path>` | `HANDLER_SUBTASKS_READY` |
| `DONE` | `HANDLER_ALL_DONE` |
| `STOP_AFTER` | `HANDLER_STOP_AFTER` |

The `Last-task` field is set at creation time — the final component (the
integration step) gets `Last-task: true`, all others get `false`. This
embeds traversal intent in the task, avoiding runtime sibling-list inspection.

See `pipeline-behavior.md` for the full traversal algorithm.

---

## NEED_HELP Handling

Any outcome ending in `_NEED_HELP` (e.g. `ARCHITECT_NEED_HELP`,
`TESTER_NEED_HELP`) is handled before the ROUTES lookup. The orchestrator
prints a message, optionally prints the job document path, and exits with
code 0. It is not an error — it signals that human intervention is required
and the pipeline is paused, not failed.

---

## Unrecognised Outcomes

If an outcome is not present in the ROUTES table and is not `NEED_HELP`, the
orchestrator halts with exit code 1 and logs the unrecognised value. This
catches cases where an agent emits a malformed or unexpected OUTCOME string.

---

## DOCUMENTER Hook *(planned, not yet implemented)*

In TM mode, the orchestrator inserts a DOCUMENTER post-step between certain
roles and their routing destination. DOCUMENTER is not a node in the ROUTES
table — it is managed directly by the orchestrator loop.

**Trigger config:**
```python
DOCUMENTER_TRIGGERS = {"ARCHITECT", "IMPLEMENTOR", "TESTER"}
```

Handlers (`DECOMPOSE_HANDLER`, `LEAF_COMPLETE_HANDLER`) are excluded — they update task
metadata only and produce no documentation artifacts.

**Hook logic:**
```
1. Role completes → outcome and DOCS field parsed
2. next_role = ROUTES[(current_role, outcome)]   ← saved as pending
3. if current_role in DOCUMENTER_TRIGGERS and DOCS is non-empty:
       run DOCUMENTER with context:
         - which role just ran
         - job document path
         - output directory
         - HANDOFF text from triggering role
         - DOCS instructions from triggering role
4. route to pending next_role
```

DOCUMENTER receives the `DOCS:` field written by the triggering role.
The content producer — not DOCUMENTER — decides what documentation is needed
and provides instructions. DOCUMENTER executes those instructions.

If `DOCS:` is absent or `none`, step 3 is skipped entirely.

---

## Agent Assignment

```python
AGENTS = {
    "DECOMPOSE_HANDLER":     "claude",
    "LEAF_COMPLETE_HANDLER": "claude",
    "ARCHITECT":             "claude",
    "IMPLEMENTOR":           "claude",
    "TESTER":                "claude",
}
```

Agent assignment is a static configuration. The orchestrator looks up the
agent name for the current role and passes it to `agent_wrapper.run_agent()`.
