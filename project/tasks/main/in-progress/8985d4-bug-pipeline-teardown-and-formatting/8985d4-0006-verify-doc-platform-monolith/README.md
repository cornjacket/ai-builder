# Task: verify-doc-platform-monolith

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 8985d4-bug-pipeline-teardown-and-formatting             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Verify the teardown fix for the `doc-platform-monolith` regression. Both the
happy-path (single-session) and the resume path must be tested.

## Context

Same test plan as 0005 (verify-doc-user-service), applied to `doc-platform-monolith`.

The root integrate task is `3ef244-0002-integrate` inside `3ef244-0000-doc-1`.

**Phase 1 — happy path**

1. `tests/regression/doc-platform-monolith/reset.sh`
2. `tests/regression/doc-platform-monolith/run.sh`
3. Verify `X-3ef244-0000-doc-1/README.md` contains `## Run Summary`
4. Verify all subtasks show `[x]`
5. Verify the Execution Log uses the `Outcome` column (not `Ended`)
6. Run gold tests: `cd tests/regression/doc-platform-monolith/gold && go test ./...`

**Phase 2 — resume path**

After Phase 1:

1. Rename `X-3ef244-0000-doc-1` → `3ef244-0000-doc-1`
2. Inside, rename `X-3ef244-0002-integrate` → `3ef244-0002-integrate`
3. In `3ef244-0002-integrate/task.json`: set `"status": "—"`
4. In `3ef244-0000-doc-1/task.json`: set `subtasks[2].complete = false`, remove `"run_summary"`
5. Remove `## Run Summary` block from `3ef244-0000-doc-1/README.md` if present
6. Write `current-job.txt` → path to `3ef244-0002-integrate/README.md`

Then resume:

7. `tests/regression/doc-platform-monolith/run.sh`
8. Verify `X-3ef244-0000-doc-1/README.md` contains `## Run Summary`
9. Verify all subtasks show `[x]`
10. Run gold tests: `cd tests/regression/doc-platform-monolith/gold && go test ./...`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
