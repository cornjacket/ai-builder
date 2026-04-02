# Task: verify-platform-monolith

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

Verify the teardown fix for the `platform-monolith` (builder pipeline) regression.
Both the happy-path (single-session) and the resume path must be tested.

## Context

Same test plan as 0005, applied to `platform-monolith`. This is a builder pipeline
(not doc), so the integrate task uses TESTER → LEAF_COMPLETE_HANDLER rather than
POST_DOC_HANDLER. The root cause and fix are identical.

The root integrate task is `650c9b-0002-integrate` inside `650c9b-0000-build-1`.

**Phase 1 — happy path**

1. `tests/regression/platform-monolith/reset.sh`
2. `tests/regression/platform-monolith/run.sh`
3. Verify `X-650c9b-0000-build-1/README.md` contains `## Run Summary`
4. Verify all subtasks show `[x]`
5. Verify the Execution Log uses the `Outcome` column (not `Ended`)
6. Run gold tests: `cd tests/regression/platform-monolith/gold && go test ./...`

**Phase 2 — resume path**

After Phase 1:

1. Rename `X-650c9b-0000-build-1` → `650c9b-0000-build-1`
2. Inside, rename `X-650c9b-0002-integrate` → `650c9b-0002-integrate`
3. In `650c9b-0002-integrate/task.json`: set `"status": "—"`
4. In `650c9b-0000-build-1/task.json`: set `subtasks[2].complete = false`, remove `"run_summary"`
5. Remove `## Run Summary` block from `650c9b-0000-build-1/README.md` if present
6. Write `current-job.txt` → path to `650c9b-0002-integrate/README.md`

Then resume:

7. `tests/regression/platform-monolith/run.sh`
8. Verify `X-650c9b-0000-build-1/README.md` contains `## Run Summary`
9. Verify all subtasks show `[x]`
10. Run gold tests: `cd tests/regression/platform-monolith/gold && go test ./...`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
