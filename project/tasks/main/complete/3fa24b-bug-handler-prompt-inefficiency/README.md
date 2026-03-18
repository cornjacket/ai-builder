# Task: bug-handler-prompt-inefficiency

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Priority    | HIGH        |
| Next-subtask-id | 0005 |

## Goal

Fix two prompt inefficiencies in DECOMPOSE_HANDLER and LEAF_COMPLETE_HANDLER that cause
unnecessary token consumption and tool call overhead, which compounds on every invocation
in long pipeline runs.

## Context

**Problem 1: Handlers receive the full accumulated handoff history.**

Every prompt is built by `build_prompt()` in `orchestrator.py`, which appends all prior
agent handoff notes as "## Handoff Notes from Previous Agents". For ARCHITECT/IMPLEMENTOR/
TESTER this is useful context. For handlers it is pure overhead — they run shell scripts,
not design decisions. By invocation 20 in a platform-monolith run, the handoff section
was ~550,000 input tokens. In a 50-invocation run this compounds further. The handlers
need zero context from prior agents.

**Problem 2: "Refer to README" line invites exploration.**

Both handler prompts end with:
  `Refer to {TARGET_REPO}/project/tasks/README.md for task system documentation.`
This is interpreted as permission (or instruction) to read a large file. Combined with
the STOP_AFTER case (which asks the agent to gather HANDOFF content about what was
implemented and TESTER results), the agent ends up reading files, listing tasks, and
exploring context it doesn't need. Result: 19 tool calls for what should be 1.

**Fix:**
1. Do not pass handoff_history to handler roles in build_prompt().
2. Remove the "Refer to README" line from both handler prompts.
3. Simplify STOP_AFTER HANDOFF instruction — agent already has task name from
   current_job_path; no file reading required.

**Observed data point:**
```
20    LEAF_COMPLETE_HANDLER    claude    integrate    22:23:15    2m 18s    19    7,437    550,802
```
LEAF_COMPLETE_HANDLER on `integrate` subtask (invocation 20, platform-monolith run):
2m 18s, 19 tool calls, 550,802 input tokens, 7,437 output tokens.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [ ] [3fa24b-0000-review-handoff-accumulation-mechanism](3fa24b-0000-review-handoff-accumulation-mechanism/)
- [ ] [3fa24b-0001-document-anthropic-cost-structure](3fa24b-0001-document-anthropic-cost-structure/)
- [ ] [3fa24b-0002-add-token-usage-regression-baseline](3fa24b-0002-add-token-usage-regression-baseline/)
- [ ] [3fa24b-0003-write-handoff-stack-algorithm-doc](3fa24b-0003-write-handoff-stack-algorithm-doc/)
- [ ] [3fa24b-0004-tester-must-not-call-task-scripts](3fa24b-0004-tester-must-not-call-task-scripts/)
<!-- subtask-list-end -->

## Notes

_None._
