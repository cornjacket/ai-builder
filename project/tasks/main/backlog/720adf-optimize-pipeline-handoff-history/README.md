# Task: optimize-pipeline-handoff-history

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Next-subtask-id | 0001 |

## Goal

Reduce the handoff history passed to IMPLEMENTOR and other roles by
trimming it to only the context that is actually relevant, rather than
the full lineage of all ancestor ARCHITECT and DECOMPOSE handoffs.

## Context

The frame_stack mechanism already scopes history per decomposition level
(sibling components don't bleed into each other). The remaining
opportunity is within a single component's execution: IMPLEMENTOR
currently receives the full ancestor chain
(ARCH/root + DECOMPOSE/root + ARCH/parent + DECOMPOSE/parent + ARCH/component).
For a 2-level tree this is 3–5 entries; for deeper trees it grows further.

From `b14e76-brainstorm-token-usage-and-caching-costs` (Opportunity 2):
medium impact (depth-dependent), medium risk (IMPLEMENTOR may need the
parent decomposition rationale to understand component boundaries).

The per-role `no_history` flag already exists in the machine JSON. This
task extends that concept with a `handoff_depth` or equivalent
per-role limit, or a role-specific filter.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [ ] [720adf-0000-implementor-trim-to-current-architect-only](720adf-0000-implementor-trim-to-current-architect-only/)
<!-- subtask-list-end -->

## Notes

_None._
