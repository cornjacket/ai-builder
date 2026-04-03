# Task: pipeline-record-replay

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | in-progress |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Next-subtask-id | 0012 |

## Goal

Design and implement a record/replay mode for the pipeline orchestrator. Record
mode captures AI output after each invocation so that the full pipeline can be
replayed without any AI calls — enabling zero-cost regression testing and
deterministic resume testing.

## Context

The AI is the expensive, slow, non-deterministic part of the pipeline. Everything
else — handlers, task advancement, metrics, README rendering, teardown — is pure
deterministic code. Record/replay decouples testing of that code from AI
availability and cost.

The orchestrator and the AI are currently tightly coupled: you can't exercise
orchestrator logic without paying for AI tokens and waiting for a non-deterministic
result. Record/replay cuts that coupling.

**What it enables:**

- **Zero-cost regression runs** — replay a reference recording to test orchestrator
  mechanics without any AI calls
- **Deterministic tests** — a gold test failure means the orchestrator changed, not
  the AI
- **Fast iteration** — verify an orchestrator fix in seconds, not 10–30 minutes
- **Precise resume testing** — replay to any mid-run state, then test resume from
  that exact point; no need to engineer a crash scenario manually
- **Prompt change visibility** — a recording is implicitly tied to the prompts used;
  changing a prompt forces a re-record, making the change explicit

The teardown bug fixed in `8985d4-bug-pipeline-teardown-and-formatting` is the
clearest example of the gap: reproducing it required a real interrupted run at
exactly the right moment. With replay, you would check out the recording at the
`HANDLER_INTEGRATE_READY` commit and run the orchestrator forward from there.

Initial brainstorm: `sandbox/brainstorms/brainstorm-pipeline-stop-and-replay.md`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [ ] [4603fa-0000-brainstorm-design](4603fa-0000-brainstorm-design/)
- [x] [X-4603fa-0001-implement-record-mode](X-4603fa-0001-implement-record-mode/)
- [x] [X-4603fa-0002-implement-halt-mechanism](X-4603fa-0002-implement-halt-mechanism/)
- [x] [X-4603fa-0003-implement-replay-mode](X-4603fa-0003-implement-replay-mode/)
- [x] [X-4603fa-0004-add-snapshot-comparison-utility](X-4603fa-0004-add-snapshot-comparison-utility/)
- [x] [X-4603fa-0005-write-replay-regression-test](X-4603fa-0005-write-replay-regression-test/)
- [x] [X-4603fa-0006-write-documentation](X-4603fa-0006-write-documentation/)
- [x] [X-4603fa-0007-delete-brainstorm](X-4603fa-0007-delete-brainstorm/)
- [ ] [4603fa-0008-store-hex-id-in-manifest](4603fa-0008-store-hex-id-in-manifest/)
- [ ] [4603fa-0009-add-id-flag-to-new-user-task](4603fa-0009-add-id-flag-to-new-user-task/)
- [ ] [4603fa-0010-update-reset-to-pin-task-id](4603fa-0010-update-reset-to-pin-task-id/)
- [ ] [4603fa-0011-enable-target-snapshot-comparison](4603fa-0011-enable-target-snapshot-comparison/)
<!-- subtask-list-end -->

## Notes

_None._
