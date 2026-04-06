# Task: establish-regression-recordings

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | in-progress |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | regression-infra       |
| Created     | 2026-04-04            |
| Completed   | —                      |
| Next-subtask-id | 0015 |

## Goal

For every full pipeline regression test, establish a recording in the
`ai-builder-recordings` repo, add `record.sh` and `test-replay.sh` scripts,
and record the first run in `runs/run-history.md`. After this task is complete,
every regression can be run as a zero-cost replay.

## Context

`user-service` is the template — it already has `record.sh`, `test-replay.sh`,
and is registered in `ai-builder-recordings`. All other full pipeline regressions
need the same treatment.

**Excluded:** `infra-smoke` (validates goldutil framework only, no pipeline run)
and `goldutil` (library, not a test).

**Per subtask, the steps are:**
1. Add `record.sh` and `test-replay.sh` modeled on `tests/regression/user-service/`
2. Ensure `runs/run-history.md` exists (create if missing)
3. Run the regression once with `--record-to <test-name>` to capture all AI
   cycles as commits in the `ai-builder-recordings` repo
4. Run gold tests; record pass/fail
5. Append a row to `runs/run-history.md`
6. Register the recording: `bash tests/regression/register-replay-test.sh --test <name> --description "..."`
7. Commit `record.sh`, `test-replay.sh`, `runs/run-history.md`

**Note:** `fibonacci` and `template-setup` have `reset.sh` but no `run.sh` —
confirm the correct invocation pattern before running.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-ccf4a4-0000-abstract-record-replay-scripts](X-ccf4a4-0000-abstract-record-replay-scripts/)
- [x] [X-ccf4a4-0001-record-platform-monolith](X-ccf4a4-0001-record-platform-monolith/)
- [x] [X-ccf4a4-0002-add-update-run-history-script](X-ccf4a4-0002-add-update-run-history-script/)
- [x] [X-ccf4a4-0003-record-doc-platform-monolith](X-ccf4a4-0003-record-doc-platform-monolith/)
- [x] [X-ccf4a4-0004-record-doc-user-service](X-ccf4a4-0004-record-doc-user-service/)
- [x] [X-ccf4a4-0014-add-recordings-status-check-script](X-ccf4a4-0014-add-recordings-status-check-script/)
<!-- subtask-list-end -->

## Notes

_None._
