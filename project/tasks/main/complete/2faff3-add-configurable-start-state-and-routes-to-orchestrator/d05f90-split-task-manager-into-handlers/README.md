# Task: split-task-manager-into-handlers

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | PIPELINE-SUBTASK       |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 2faff3-add-configurable-start-state-and-routes-to-orchestrator             |
| Priority    | —           |
| Complexity  | —                      |
| Stop-after  | false                  |
| Last-task   | false                  |
| Level       | INTERNAL              |

## Goal

Split the single `TASK_MANAGER` role into two distinct roles:
`DECOMPOSE_HANDLER` and `LEAF_COMPLETE_HANDLER`.

## Context

The current `TASK_MANAGER` prompt builder has two completely different
behaviors selected by a runtime `last_outcome` check:

- `last_outcome == "ARCHITECT_DECOMPOSITION_READY"` → reads the
  Components table, creates subtasks, points pipeline at the first one
- else → runs `on-task-complete.sh`, interprets NEXT/DONE/STOP_AFTER

These are different jobs sharing a role name. The `last_outcome` check
is a code smell that prevents the pipeline from being expressed as a
clean state machine — a single role cannot have two prompt files or two
sets of valid outcomes.

**`DECOMPOSE_HANDLER`**: triggered after ARCHITECT decomposes a service.
Reads Components table, creates pipeline subtasks, sets Last-task and
Level on the integrate component, points pipeline at first subtask.
Valid outcomes: `TM_SUBTASKS_READY`, `TM_NEED_HELP`.

**`LEAF_COMPLETE_HANDLER`**: triggered after TESTER passes on a leaf
task. Calls `on-task-complete.sh`, interprets the result.
Valid outcomes: `TM_SUBTASKS_READY`, `TM_ALL_DONE`, `TM_STOP_AFTER`,
`TM_NEED_HELP`.

The transition table becomes:
- `ARCHITECT → ARCHITECT_DECOMPOSITION_READY → DECOMPOSE_HANDLER`
- `DECOMPOSE_HANDLER → TM_SUBTASKS_READY → ARCHITECT`
- `TESTER → TESTER_TESTS_PASS → LEAF_COMPLETE_HANDLER`
- `LEAF_COMPLETE_HANDLER → TM_SUBTASKS_READY → ARCHITECT`
- `LEAF_COMPLETE_HANDLER → TM_ALL_DONE → halt`

This must be done before `d21b9d-implement-state-machine` so the state
machine file can properly describe all roles without exceptions.

## Components

_To be completed by the ARCHITECT._

## Design

_To be completed by the ARCHITECT._

## Acceptance Criteria

_To be completed by the ARCHITECT._

## Suggested Tools

_To be completed by the ARCHITECT._

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

### Implementation Plan

**Step 1 — Rename outcome strings**

`TM_` prefix is tied to `TASK_MANAGER` which is going away. Rename
everywhere they appear (orchestrator.py, routing.md, pipeline-behavior.md):

| Old | New |
|-----|-----|
| `TM_SUBTASKS_READY` | `HANDLER_SUBTASKS_READY` |
| `TM_ALL_DONE`       | `HANDLER_ALL_DONE`       |
| `TM_STOP_AFTER`     | `HANDLER_STOP_AFTER`     |
| `TM_NEED_HELP`      | `HANDLER_NEED_HELP`      |

**Step 2 — Split `AGENTS` dict**

Remove `"TASK_MANAGER": "claude"`.
Add `"DECOMPOSE_HANDLER": "claude"` and `"LEAF_COMPLETE_HANDLER": "claude"`.

**Step 3 — Split `build_prompt()` TM branch**

Replace the single `if role == "TASK_MANAGER"` branch (which selects
behaviour via `last_outcome`) with two independent branches:

- `if role == "DECOMPOSE_HANDLER"` — current `ARCHITECT_DECOMPOSITION_READY`
  sub-branch verbatim; valid outcomes: `HANDLER_SUBTASKS_READY | HANDLER_NEED_HELP`
- `elif role == "LEAF_COMPLETE_HANDLER"` — current `else` sub-branch verbatim;
  valid outcomes: `HANDLER_SUBTASKS_READY | HANDLER_ALL_DONE | HANDLER_STOP_AFTER | HANDLER_NEED_HELP`

The `if last_outcome == "ARCHITECT_DECOMPOSITION_READY":` check is deleted.

**Step 4 — Update `ROUTES` (TM mode additions)**

```
("ARCHITECT",             "ARCHITECT_DECOMPOSITION_READY") → "DECOMPOSE_HANDLER"
("DECOMPOSE_HANDLER",     "HANDLER_SUBTASKS_READY")        → "ARCHITECT"
("DECOMPOSE_HANDLER",     "HANDLER_NEED_HELP")             → None
("TESTER",                "TESTER_TESTS_PASS")             → "LEAF_COMPLETE_HANDLER"
("LEAF_COMPLETE_HANDLER", "HANDLER_SUBTASKS_READY")        → "ARCHITECT"
("LEAF_COMPLETE_HANDLER", "HANDLER_ALL_DONE")              → None
("LEAF_COMPLETE_HANDLER", "HANDLER_STOP_AFTER")            → None
("LEAF_COMPLETE_HANDLER", "HANDLER_NEED_HELP")             → None
```

**Step 5 — Update `current_role == "TASK_MANAGER"` guard**

Line ~336 in orchestrator.py reads current-job.txt after a handler
signals `HANDLER_SUBTASKS_READY`. Update the condition:

```python
# Before:
if current_role == "TASK_MANAGER" and outcome == "TM_SUBTASKS_READY":
# After:
if current_role in ("DECOMPOSE_HANDLER", "LEAF_COMPLETE_HANDLER") \
        and outcome == "HANDLER_SUBTASKS_READY":
```

**Step 6 — Update docs**

- `routing.md` — rewrite route table with new role names and outcome strings
- `pipeline-behavior.md` — update role descriptions and outcome strings
- `ai-builder/orchestrator/README.md` — update agent list
