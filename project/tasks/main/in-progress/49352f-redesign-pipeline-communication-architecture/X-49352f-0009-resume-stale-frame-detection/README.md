# Task: resume-stale-frame-detection

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

At startup, when `handoff-state.json` is loaded (via `--handoff-file` or
`--resume` auto-load), detect a stale component frame on the top of
`frame_stack` and recover automatically: pop the frame, truncate
`handoff_history` to the anchor, and print a clear warning to stdout that
the pipeline is resuming from an incomplete state.

## Context

If an agent emits NEED_HELP or the pipeline is interrupted after a component
frame has been pushed but before LCH fires (i.e. before TESTER passes),
`handoff-state.json` is written with the component frame still on the stack.
On the next run that loads this file, the stale frame would cause the resumed
ARCHITECT to see its own prior incomplete design attempt in the handoff history
— polluting the prompt with a failed or partial entry.

**Detection condition:** the top frame in `frame_stack` is `type: "component"`
AND the corresponding component's `task.json` does not have `complete: true`.

**Recovery:**
1. Pop the stale component frame
2. Truncate `handoff_history` to `frame["anchor_index"] + 1` (restores history
   to the clean state just before that component's ARCHITECT ran)
3. Print a warning:
   ```
   [orchestrator] WARNING: stale component frame detected for '{component_name}'.
       The previous run did not complete this component cleanly (NEED_HELP or interrupt).
       Truncating handoff history to the pre-component anchor and retrying.
   ```

The resumed ARCHITECT then receives the same history it would have seen on a
clean first attempt for that component — no contamination from the prior run.

**Dependency:** subtask 0008 (handoff-state-persist-and-inject) must be
complete before this subtask — it provides the `--handoff-file` load path
where this check runs. Subtask 0005 (handoff-frame-stack-redesign) must also
be complete, as it defines the `type: "component"` frame structure.

**Sequence position:** immediately after 0008 in the implementation order.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
