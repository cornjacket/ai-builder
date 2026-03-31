# Routing

The orchestrator routes between roles using a lookup table keyed on
`(current_role, outcome)`. Each entry maps to either the next role name
or `None` (halt).

---

## ROUTES Table

The state machine is defined in `machines/builder/default.json` (TM mode) and
`machines/builder/simple.json` (non-TM / single-step mode). The tables below reflect
the current `default.json` and `simple.json` configurations.

### TM Mode (`machines/builder/default.json`)

| From | Outcome | To |
|------|---------|----|
| ARCHITECT | `ARCHITECT_DESIGN_READY` | DOCUMENTER_POST_ARCHITECT |
| ARCHITECT | `ARCHITECT_DECOMPOSITION_READY` | DECOMPOSE_HANDLER |
| ARCHITECT | `ARCHITECT_NEEDS_REVISION` | ARCHITECT *(self-loop)* |
| ARCHITECT | `ARCHITECT_NEED_HELP` | halt |
| DOCUMENTER_POST_ARCHITECT | `DOCUMENTER_DONE` | IMPLEMENTOR |
| IMPLEMENTOR | `IMPLEMENTOR_IMPLEMENTATION_DONE` | DOCUMENTER_POST_IMPLEMENTOR |
| IMPLEMENTOR | `IMPLEMENTOR_NEEDS_ARCHITECT` | ARCHITECT |
| IMPLEMENTOR | `IMPLEMENTOR_NEED_HELP` | halt |
| DOCUMENTER_POST_IMPLEMENTOR | `DOCUMENTER_DONE` | TESTER |
| TESTER | `TESTER_TESTS_PASS` | LEAF_COMPLETE_HANDLER |
| TESTER | `TESTER_TESTS_FAIL` | IMPLEMENTOR |
| TESTER | `TESTER_NEED_HELP` | halt |
| DECOMPOSE_HANDLER | `HANDLER_SUBTASKS_READY` | ARCHITECT |
| DECOMPOSE_HANDLER | `HANDLER_STOP_AFTER` | halt |
| DECOMPOSE_HANDLER | `HANDLER_NEED_HELP` | halt |
| LEAF_COMPLETE_HANDLER | `HANDLER_SUBTASKS_READY` | ARCHITECT |
| LEAF_COMPLETE_HANDLER | `HANDLER_ALL_DONE` | halt *(post-completion flow runs first)* |
| LEAF_COMPLETE_HANDLER | `HANDLER_STOP_AFTER` | halt *(Oracle intervention required)* |
| LEAF_COMPLETE_HANDLER | `HANDLER_NEED_HELP` | halt |

### Non-TM / Single-Step Mode (`machines/builder/simple.json`)

| From | Outcome | To |
|------|---------|----|
| ARCHITECT | `ARCHITECT_DESIGN_READY` | DOCUMENTER_POST_ARCHITECT |
| ARCHITECT | `ARCHITECT_NEED_HELP` | halt |
| DOCUMENTER_POST_ARCHITECT | `DOCUMENTER_DONE` | IMPLEMENTOR |
| IMPLEMENTOR | `IMPLEMENTOR_IMPLEMENTATION_DONE` | DOCUMENTER_POST_IMPLEMENTOR |
| IMPLEMENTOR | `IMPLEMENTOR_NEEDS_ARCHITECT` | ARCHITECT |
| IMPLEMENTOR | `IMPLEMENTOR_NEED_HELP` | halt |
| DOCUMENTER_POST_IMPLEMENTOR | `DOCUMENTER_DONE` | TESTER |
| TESTER | `TESTER_TESTS_PASS` | halt *(pipeline complete)* |
| TESTER | `TESTER_TESTS_FAIL` | IMPLEMENTOR |
| TESTER | `TESTER_NEED_HELP` | halt |

Simple mode has no DECOMPOSE_HANDLER or LEAF_COMPLETE_HANDLER — it handles
a single atomic job from a `--job` file.

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

## DOCUMENTER Agents

`DOCUMENTER_POST_ARCHITECT` and `DOCUMENTER_POST_IMPLEMENTOR` are internal
agents — they run Python code directly without invoking a model. Both are
nodes in the state machine (see ROUTES tables above).

**What they do:**
1. Read `documents_written` from `task.json`. If `false` or absent → return
   `DOCUMENTER_DONE` immediately (no-op).
2. Walk the output directory for `*.md` files with `Purpose:` / `Tags:` headers
   (excluding root `README.md` and `master-index.md`).
3. Rebuild the output directory's `README.md` with a documentation index
   (design docs from ARCHITECT, implementation docs from IMPLEMENTOR).

Handlers (`DECOMPOSE_HANDLER`, `LEAF_COMPLETE_HANDLER`) are excluded — they
update task metadata only and produce no documentation artifacts.

---

## Agent Assignment

Agent types are declared per-role in the machine JSON (`"agent": "claude"` or
`"agent": "internal"`). Internal agents run Python functions directly; AI
agents spawn a subprocess via `agent_wrapper.py`.

| Role | Agent type |
|------|-----------|
| ARCHITECT | claude (or gemini) |
| IMPLEMENTOR | claude (or gemini) |
| TESTER | internal |
| DECOMPOSE_HANDLER | internal |
| LEAF_COMPLETE_HANDLER | internal |
| DOCUMENTER_POST_ARCHITECT | internal |
| DOCUMENTER_POST_IMPLEMENTOR | internal |
