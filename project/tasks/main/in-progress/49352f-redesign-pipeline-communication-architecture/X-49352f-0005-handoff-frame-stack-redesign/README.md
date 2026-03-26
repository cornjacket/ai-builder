# Task: handoff-frame-stack-redesign

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 49352f-redesign-pipeline-communication-architecture             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Replace the single-type frame stack with two frame types (`decompose` and
`component`) so that `handoff_history` is level-scoped: each agent sees the
decomposition context from its parent level and compact completion summaries
from finished siblings, but nothing from inside a sibling's A→I→T cycle.

## Context

The current frame stack uses a `scope_dir` equality check that never matches
any sibling transition. Every LCH invocation clears `handoff_history`
completely. Each component starts with zero context — ARCHITECT for
`build-1/integrate` has no record that metrics or iam completed, or where
their source files live.

Full design and history walk-through:
`sandbox/brainstorm-handoff-frame-stack-redesign.md`

**Changes required:**

1. **Two frame types** — replace the single frame dict with:
   - `{"type": "decompose", "anchor_index": N}` — pushed by
     DECOMPOSE_HANDLER; popped by LCH when `last-task=true`
   - `{"type": "component", "anchor_index": N, "component_name": X}` —
     pushed by the orchestrator just before ARCHITECT runs in atomic/design
     mode; popped by LCH after every TESTER pass

2. **LCH two-phase pop** — after each TESTER pass:
   - Always pop the component frame; truncate history to the anchor;
     append `[{component} complete] {output_dir}`
   - If `last-task=true`: also pop the decompose frame; truncate further;
     append a level summary combining all component completion entries

3. **Retire `scope_dir`** — the field is unused once the new logic is in
   place. Remove it from the frame dict.

4. **`output_dir` source** — read from `task.json` (set by DECOMPOSE_HANDLER
   in subtask 0003). No AI return value needed.

**Dependency:** subtask 0003 (DECOMPOSE_HANDLER writes `output_dir` to
`task.json`) must be complete before this subtask is implemented. This subtask
must be complete before subtask 0014 (handoff-state persist/inject), which
serializes the frame stack structure.

**Sequence position:** between 0008 and 0014 in the implementation order.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
