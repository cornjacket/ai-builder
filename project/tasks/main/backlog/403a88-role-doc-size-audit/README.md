# Task: role-doc-size-audit

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | acceptance-spec        |
| Next-subtask-id | 0001 |

## Goal

Measure the size of all role prompt documents (`roles/*.md`) and trim any
that are verbose without adding agent behaviour value. Smaller role docs
reduce the fixed per-invocation token cost for every agent call.

## Context

Role docs (ARCHITECT.md, IMPLEMENTOR.md, TESTER.md, etc.) are injected
verbatim into every invocation of their role. Their sizes have not been
systematically measured. If any contain lengthy examples, redundant
instructions, or prose that doesn't change agent behaviour, trimming them
reduces the per-invocation cached token floor for every future run.

From `b14e76-brainstorm-token-usage-and-caching-costs` (Opportunity 5):
estimated impact is small but the effort is also minimal.

**Implementation:**
1. Run `wc -c roles/*.md` to measure sizes
2. Review each doc for content that can be removed without affecting agent behaviour
3. Trim and re-run a regression to confirm token reduction
4. Compare results against historical baseline (subtask 0000)

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [ ] [403a88-0000-compare-token-usage-with-historical-runs](403a88-0000-compare-token-usage-with-historical-runs/)
<!-- subtask-list-end -->

## Notes

_None._
