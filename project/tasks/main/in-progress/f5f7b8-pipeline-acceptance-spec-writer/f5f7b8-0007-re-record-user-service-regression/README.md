# Task: re-record-user-service-regression

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | f5f7b8-pipeline-acceptance-spec-writer             |
| Priority    | —           |
| Created     | {{CREATED}}            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Re-run the user-service regression with the f5f7b8 pipeline changes, verify
gold tests pass, and push a fresh recording to `ai-builder-recordings/user-service`.

## Context

The existing recording predates f5f7b8. The new pipeline has three additional
states (ACCEPTANCE_SPEC_WRITER, SPEC_COVERAGE_CHECKER, active_role persistence)
that any replay would diverge on. A fresh recording is required.

`record.sh --force` deletes the remote orphan branch automatically before
pushing. Run from the repo root:

```bash
bash tests/regression/user-service/record.sh --force
```

Then update `runs/run-history.md` and verify replay passes.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
