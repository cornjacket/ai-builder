# Task: bug-pipeline-teardown-and-formatting

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Next-subtask-id | 0009 |

## Goal

Investigate and fix three related pipeline bugs observed when comparing the
`user-service` build regression output against the `doc-user-service`,
`doc-platform-monolith`, and `platform-monolith` regression outputs.

## Context

Three symptoms observed:

1. **Missing run-summary table** — the `user-service` build regression
   TOP-level pipeline-subtask README contains a token/elapsed-time summary
   table; the doc and platform-monolith regressions do not. Something in
   teardown is not completing for those runs.

2. **Last pipeline-subtask not marked complete** — for the same affected
   regressions, the final pipeline-subtask directory is renamed with the
   `X-` prefix (indicating completion) but the subtask's `README.md` `Status`
   field and the parent's subtask list are not updated. This is the same
   symptom we have seen before when the orchestrator calls `exit(0)` before
   the task-management scripts finish updating the document. Issues 1 and 2
   are likely the same root cause.

3. **Top-level pipeline-task README formatting** — the top-level
   pipeline-subtask README no longer appears formatted the way it used to.
   Unclear whether this is a regression in `render_readme.py`, a change in
   how `new-pipeline-build.sh` generates the initial README, or a side effect
   of the teardown bug above.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-8985d4-0000-investigate-missing-run-summary](X-8985d4-0000-investigate-missing-run-summary/)
- [x] [X-8985d4-0001-investigate-last-subtask-not-marked-complete](X-8985d4-0001-investigate-last-subtask-not-marked-complete/)
- [x] [X-8985d4-0002-investigate-top-level-readme-formatting](X-8985d4-0002-investigate-top-level-readme-formatting/)
- [x] [X-8985d4-0003-fix-teardown-and-formatting](X-8985d4-0003-fix-teardown-and-formatting/)
- [x] [X-8985d4-0005-verify-doc-user-service](X-8985d4-0005-verify-doc-user-service/)
- [x] [X-8985d4-0006-verify-doc-platform-monolith](X-8985d4-0006-verify-doc-platform-monolith/)
- [x] [X-8985d4-0007-verify-platform-monolith](X-8985d4-0007-verify-platform-monolith/)
- [x] [X-8985d4-0008-fix-internal-readme-subtask-completion](X-8985d4-0008-fix-internal-readme-subtask-completion/)
<!-- subtask-list-end -->

## Notes

_None._
