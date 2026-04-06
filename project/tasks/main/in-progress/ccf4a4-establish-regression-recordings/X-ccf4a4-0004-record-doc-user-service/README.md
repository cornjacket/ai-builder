# Task: record-doc-user-service

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | ccf4a4-establish-regression-recordings             |
| Priority    | —           |
| Created     | 2026-04-04            |
| Completed | 2026-04-05 |
| Next-subtask-id | 0000               |

## Goal

Establish the first recording for the `doc-user-service` regression and add replay
infrastructure so future runs can execute without AI invocations.

## Context

Never run. Has reset.sh and run.sh.

**Steps:** see parent task `ccf4a4-establish-regression-recordings` for the
full per-subtask procedure.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

After pushing the recording for the first time, confirm that the
ai-builder-recordings main branch README.md Regression tests table has been
updated with a row for `doc-user-service`. Use:

```bash
bash tests/regression/lib/add-to-recordings-readme.sh \
    --name        doc-user-service \
    --description "<what this regression exercises>"
```
