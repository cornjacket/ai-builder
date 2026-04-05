# Task: re-record-user-service-regression

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | acceptance-spec        |
| Created     | 2026-04-04            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Re-run the user-service regression with the new ACCEPTANCE_SPEC_WRITER pipeline
changes (f5f7b8), verify gold tests pass, and push a fresh recording to the
`user-service` branch on `ai-builder-recordings`.

## Context

The user-service regression needs to be re-recorded because f5f7b8 changed the
builder pipeline in ways that affect every run:
- New `ACCEPTANCE_SPEC_WRITER` start state runs before ARCHITECT
- `SPEC_COVERAGE_CHECKER` runs after IMPLEMENTOR at TOP integrate level
- `active_role` is now persisted to `task.json` on each state transition

The existing recording on `ai-builder-recordings/user-service` was captured
before these changes. Any replay against the new pipeline would diverge at the
first state. A fresh recording is required.

`record.sh --force` handles the orphan branch deletion automatically —
it runs `git push origin --delete user-service || true` before pushing the new
recording. No manual branch cleanup needed.

**Steps:**
1. Run `bash tests/regression/user-service/record.sh --force` from the repo root
2. Confirm gold tests pass in the record output
3. Update `runs/run-history.md` with the new row
4. Commit `run-history.md`
5. Verify replay: `bash tests/regression/user-service/test-replay.sh`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
