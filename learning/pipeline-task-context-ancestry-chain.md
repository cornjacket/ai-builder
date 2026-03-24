# Pipeline: Task Context Ancestry Chain

## The problem

`DECOMPOSE_HANDLER` creates child subtasks and populates each child's `## Context`
by flat-copying the parent's `## Goal` + `## Context` verbatim. At shallow nesting
this works. At Level 3 and below it breaks:

- Level 2's `## Context` already contains Level 1's goal
- DECOMPOSE_HANDLER copies Level 2's `## Context` into Level 3 — so Level 3
  now contains Level 1's goal twice
- Each additional descent compounds the duplication

By Level 4 the context block is dominated by repeated text from upper levels.
The downstream ARCHITECT or IMPLEMENTOR cannot reliably identify which goal
belongs to which ancestor, and the growing context wastes tokens on noise.

---

## The fix

`DECOMPOSE_HANDLER` builds a **labelled ancestry chain** instead of flat-copying.
Each decomposition appends exactly one new entry for the current level. Earlier
entries are never re-copied.

**Child context at Level 2:**
```
### Level 2 — user-service
Build a user authentication service supporting OAuth2 and local login.
```

**Child context at Level 3:**
```
### Level 2 — user-service
Build a user authentication service supporting OAuth2 and local login.

### Level 3 — handlers
Routes incoming HTTP requests to the store and middleware components.
```

Each entry is labelled with its depth and task name. The chain grows by one
entry per descent. There is no duplication at any depth.

---

## Implementation: `depth` field in `task.json`

A `depth` field tracks numeric nesting depth. This avoids inferring depth from
the context text itself (brittle) or from directory nesting (requires filesystem
traversal).

**Schema:**
```json
{ "depth": 0 }
```

`depth: 0` is the pipeline entry point (Level:TOP), created by
`new-pipeline-subtask.sh`. DECOMPOSE_HANDLER sets `depth = parent_depth + 1`
on each child at creation time.

**Flow in `_run_decompose_internal()`:**
1. Read `parent_depth` from parent's `task.json`
2. Compute `child_depth = parent_depth + 1`
3. Extract parent's `## Goal` and existing `## Context` (the inherited chain)
4. Append `### Level {child_depth} — {parent_task_name}\n{parent_goal}` to the chain
5. Write the composed chain into each child's `## Context`
6. Set `"depth": child_depth` in each child's `task.json`

---

## Key distinction from handoff history

The ancestry chain in `## Context` is **static** — written once at task creation,
describes why the component exists and what system it is part of.

The handoff history passed to `build_prompt()` is **dynamic** — accumulated at
runtime, describes what has happened so far in the current pipeline execution.

They serve different purposes. The ancestry chain gives the agent standing context
about the system it is building a piece of. The handoff history gives it context
about the current execution state.
