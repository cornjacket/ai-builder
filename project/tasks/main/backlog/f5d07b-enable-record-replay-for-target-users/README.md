# Task: enable-record-replay-for-target-users

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | HIGH           |
| Category    | orchestrator-core      |
| Created     | 2026-04-03            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Expose the record/replay feature to target users (customers) so they can
capture a git-committed history of each agent's output in their own target
repo, enabling debugging of unexpected pipeline output or intermittent
failures.

**Depends on:** `4603fa-pipeline-record-replay` — do not start until that
feature is merged.

## Context

Motivation surfaced during `8985d4-0007-verify-platform-monolith`: a retry
occurred (IMPLEMENTOR on `store`) and the source code from the failed first
attempt was unrecoverable — the retry overwrote it in the output directory.
The record mechanism (git commit before each AI cycle) preserves every
intermediate state.

While `4603fa` implements the mechanism for internal regression use, the same
feature is valuable for end users running the pipeline against their own
systems:

- **Customer debugging** — when the pipeline produces unexpected output or a
  component fails tests intermittently, replay lets the user step through each
  agent's exact contribution
- **Isolation** — separates what the ARCHITECT designed from what the
  IMPLEMENTOR wrote from what the TESTER changed, at each task node
- **Retry forensics** — the failed attempt before a retry is preserved and
  inspectable; currently it is silently overwritten

**What this task covers:**
1. Expose record/replay as a supported mode in the orchestrator CLI (flag or
   config option) so customers can opt in
2. Document the feature in end-user-facing docs: how to enable, what gets
   committed, how to browse the history, when saving is necessary (failure or
   retry) vs optional (clean run with prior recording already saved)
3. Ensure regression reset.sh scripts optionally init a git repo in the
   output dir so internal runs also benefit

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
