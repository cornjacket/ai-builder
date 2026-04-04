# Task: parallel-component-execution

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | orchestrator-core      |
| Next-subtask-id | 0000               |

## Goal

After DECOMPOSE_HANDLER splits a composite task into N sibling components,
execute those siblings in parallel rather than sequentially. Wall time
reduction scales with the number of siblings and is independent of token
usage.

## Context

Today the orchestrator processes siblings one at a time:
ARCH → IMPL → TESTER → LCH → ARCH → IMPL → TESTER → LCH → ...

Sibling components are structurally independent — they share only the
parent job doc and the DECOMPOSE handoff, not any generated code or state.
There is no correctness reason they must run sequentially (except for
`Last-task` integrate components, which must run after all siblings
complete).

**Expected impact:** No token reduction. Wall-time reduction proportional
to decomposition width. For platform-monolith (metrics + iam as siblings):
roughly −50% of sibling processing time. For wider decompositions the
benefit scales further. Integrate tasks (Last-task) still run sequentially
after all siblings finish.

**Known complications:**
- **Shared file conflicts:** siblings may write to the same files (e.g.
  `go.mod`, shared packages). Needs a conflict detection or locking strategy.
- **Rate limit handling:** concurrent API calls multiply rate limit
  pressure. Need backoff/retry coordination across branches.
- **Handoff isolation:** each parallel branch must maintain its own
  handoff history; branches must not share state.
- **Result merge:** the orchestrator must wait for all branches to complete
  before advancing to the integrate component.
- **Metrics:** `run-metrics.json` must handle concurrent writes safely.

This is a high-complexity architectural change. Design subtasks are needed
before any implementation begins.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
