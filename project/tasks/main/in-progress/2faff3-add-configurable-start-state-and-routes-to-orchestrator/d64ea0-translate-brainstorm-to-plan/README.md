# Task: translate-brainstorm-to-plan

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 2faff3-add-configurable-start-state-and-routes-to-orchestrator             |
| Priority    | —           |

## Goal

Translate the brainstorm document into a concrete, ordered, multi-step
implementation plan suitable for Oracle review and pipeline execution.

## Context

Inputs: the brainstorm doc from `82c090` and the existing task description
in the `2faff3` README. Output: a written plan with discrete steps, each
scoped to a single change, in the order they should be implemented.
The plan should cover: orchestrator CLI changes, routes loading logic,
start-state validation, TM mode interaction rules, `--request` removal,
and any doc updates required. The plan becomes the input to `fcee0a`
(present to Oracle) and, once approved, drives the pipeline subtasks
`d21b9d` and `7a860d`.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

### Implementation Plan

Scope evolved significantly during brainstorm (`82c090`) and subsequent
design discussions. The original `--start-state` + `--routes` design grew
into: TASK_MANAGER split, `--state-machine` file format, and `--start-state`
override. Plan below reflects the full current scope.

---

#### Phase 1 — `7a860d`: Remove `--request` dead code

**What:** Delete four lines from `orchestrator.py`. No behaviour change.

```
parser.add_argument("--request", ...)           # lines 38-41
if args.request and not args.request.exists():  # lines 49-51
REQUEST = args.request.read_text() ...          # line 72
print(f"    request: ...")                       # line 294
```

**Also:** remove `--request` from `orchestrator.md`.

**Dependencies:** none. Fully independent, zero risk.

---

#### Phase 2 — `d05f90`: Split TASK_MANAGER into two handlers

**What:** Replace the single `TASK_MANAGER` role (which uses a
`last_outcome` check to select between two unrelated behaviours) with
two clean roles, each with one job and one prompt.

**Step 1 — Rename outcome strings** (everywhere in orchestrator.py,
routing.md, pipeline-behavior.md):

| Old | New |
|-----|-----|
| `TM_SUBTASKS_READY` | `HANDLER_SUBTASKS_READY` |
| `TM_ALL_DONE` | `HANDLER_ALL_DONE` |
| `TM_STOP_AFTER` | `HANDLER_STOP_AFTER` |
| `TM_NEED_HELP` | `HANDLER_NEED_HELP` |

**Step 2 — Split `AGENTS` dict:**
- Remove `"TASK_MANAGER": "claude"`
- Add `"DECOMPOSE_HANDLER": "claude"` and `"LEAF_COMPLETE_HANDLER": "claude"`

**Step 3 — Split `build_prompt()` TM branch** into two independent
branches. The `if last_outcome == "ARCHITECT_DECOMPOSITION_READY":`
check is deleted — routing now handles this distinction.

**Step 4 — Update `ROUTES`** (TM mode additions):
```
ARCHITECT / ARCHITECT_DECOMPOSITION_READY  → DECOMPOSE_HANDLER
DECOMPOSE_HANDLER / HANDLER_SUBTASKS_READY → ARCHITECT
DECOMPOSE_HANDLER / HANDLER_NEED_HELP      → None
TESTER / TESTER_TESTS_PASS                 → LEAF_COMPLETE_HANDLER
LEAF_COMPLETE_HANDLER / HANDLER_SUBTASKS_READY → ARCHITECT
LEAF_COMPLETE_HANDLER / HANDLER_ALL_DONE   → None
LEAF_COMPLETE_HANDLER / HANDLER_STOP_AFTER → None
LEAF_COMPLETE_HANDLER / HANDLER_NEED_HELP  → None
```

**Step 5 — Update `current_role == "TASK_MANAGER"` guard** (line ~336):
```python
if current_role in ("DECOMPOSE_HANDLER", "LEAF_COMPLETE_HANDLER") \
        and outcome == "HANDLER_SUBTASKS_READY":
```

**Step 6 — Update docs:** `routing.md`, `pipeline-behavior.md`,
`orchestrator/README.md`.

**Dependencies:** Phase 1 must be complete.

---

#### Phase 3 — `d21b9d`: Implement `--state-machine` and `--start-state`

**What:** Externalise the pipeline's state machine into a JSON file.
Add `--state-machine` to load a custom machine; add `--start-state` to
override the machine's declared entry point at runtime.

**Step 1 — Define the machine file format:**

```json
{
  "start_state": "ARCHITECT",
  "roles": {
    "ARCHITECT":            { "agent": "claude", "prompt": "roles/ARCHITECT.md" },
    "IMPLEMENTOR":          { "agent": "claude", "prompt": "roles/IMPLEMENTOR.md" },
    "TESTER":               { "agent": "claude", "prompt": "roles/TESTER.md" },
    "DECOMPOSE_HANDLER":    { "agent": "claude", "prompt": null },
    "LEAF_COMPLETE_HANDLER":{ "agent": "claude", "prompt": null }
  },
  "transitions": {
    "ARCHITECT": {
      "ARCHITECT_DESIGN_READY":        "IMPLEMENTOR",
      "ARCHITECT_DECOMPOSITION_READY": "DECOMPOSE_HANDLER",
      "ARCHITECT_NEEDS_REVISION":      "ARCHITECT",
      "ARCHITECT_NEED_HELP":           null
    },
    ...
  }
}
```

`prompt: null` means the orchestrator uses its built-in dynamic
generation for that role (DECOMPOSE_HANDLER and LEAF_COMPLETE_HANDLER
both have runtime variables injected into their prompts).

**Step 2 — Create `machines/` directory** with two committed files:
- `machines/default.json` — full pipeline (ARCHITECT + IMPLEMENTOR +
  TESTER + DECOMPOSE_HANDLER + LEAF_COMPLETE_HANDLER, start: ARCHITECT)
- `machines/simple.json` — flat mode (ARCHITECT + IMPLEMENTOR + TESTER,
  TESTER_TESTS_PASS → null, start: ARCHITECT)

**Step 3 — Add `--state-machine` CLI flag:**
```python
parser.add_argument("--state-machine", type=Path, metavar="FILE")
```
Optional. When omitted: orchestrator infers default machine
(`machines/default.json` if `--target-repo` present, else
`machines/simple.json`).

**Step 4 — Add `--start-state` CLI flag:**
```python
parser.add_argument("--start-state", metavar="ROLE")
```
Optional. Overrides `start_state` from the loaded machine file.
Valid values: any role in the loaded machine's `roles` section.

**Step 5 — Add `load_state_machine()` function:**
Loads JSON, validates: all roles in transitions exist in roles section;
all next-role values (non-null) exist in roles section; `start_state`
exists in roles section. Builds `AGENTS` dict and `ROUTES` dict from
the loaded data.

**Step 6 — Replace hardcoded `AGENTS` and `ROUTES`** with values
loaded from the machine file.

**Step 7 — `_NEED_HELP` interception remains unconditional** regardless
of machine file contents. Safety invariant, not configurable.

**Step 8 — Update docs:** `orchestrator.md` with new flags, machine
file format, and example invocations.

**Dependencies:** Phase 2 must be complete (machine file needs clean
role names — no TASK_MANAGER).

---

#### Phase 4 — `ec4004`: Regression tests

Scenarios to verify:
1. Default behaviour unchanged: no `--state-machine` or `--start-state`
   flags, pipeline runs identical to before
2. `--start-state TESTER`: starts at TESTER against existing output
   from a known regression test
3. `--state-machine machines/simple.json`: flat mode pipeline runs and
   halts after TESTER_TESTS_PASS
4. Invalid `--start-state`: role not in machine → clear error, exit 1
5. Invalid `--state-machine`: malformed JSON → clear error, exit 1

**Dependencies:** Phase 3 must be complete.

---

#### Phase 5 — `00f0ec`: Update `a09648-optimize-pipeline-tm-prompt`

Rewrite the backlog task to reflect the handler split. "Branch A" →
`DECOMPOSE_HANDLER`, "Branch B" → `LEAF_COMPLETE_HANDLER`. The
two-branch problem is already solved; update the task to focus on
the remaining optimisation opportunities (scripting DECOMPOSE_HANDLER
bookkeeping).

**Dependencies:** Phase 2 must be complete.

---

#### Open questions for Oracle review (from brainstorm)

1. `--start-state DECOMPOSE_HANDLER` / `LEAF_COMPLETE_HANDLER` — useful
   or explicitly disallowed? These handlers expect specific pre-conditions
   (pre-seeded `current-job.txt`). Recommend: allow but document.

2. Missing role warning vs error — if a role in the machine file's
   `roles` section has no entries in `transitions`, warn or error?
   Recommendation: warn only (role may be intentionally unreachable).

3. Confirm `prompt: null` convention for dynamic prompts is acceptable,
   vs a future templating system.
