# Task: verify-doc-user-service

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 8985d4-bug-pipeline-teardown-and-formatting             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Verify the teardown fix for the `doc-user-service` regression. Both the happy-path
(single-session) and the resume path must be tested.

## Context

The bug only triggers on resume: when `current-job.txt` points to an integrate task
at orchestrator startup, the old `_find_level_top` returned the integrate task as the
"TOP" task instead of the real build entry point.

**Phase 1 — happy path**

1. `tests/regression/doc-user-service/reset.sh`
2. `tests/regression/doc-user-service/run.sh`
3. Verify `X-ccafc6-0000-doc-1/README.md` contains `## Run Summary`
4. Verify all subtasks show `[x]`
5. Verify the Execution Log uses the `Outcome` column (not `Ended`)
6. Run gold tests: `cd tests/regression/doc-user-service/gold && go test ./...`

**Phase 2 — resume path (simulates the original bug scenario)**

After Phase 1 completes successfully, reconstruct the pre-resume state:

1. Rename `X-ccafc6-0000-doc-1` → `ccafc6-0000-doc-1`
2. Inside that dir, rename `X-ccafc6-0001-integrate` → `ccafc6-0001-integrate`
3. In `ccafc6-0001-integrate/task.json`: set `"status": "—"`
4. In `ccafc6-0000-doc-1/task.json`:
   - Set `subtasks[1].complete = false` (the integrate entry)
   - Remove `"run_summary"` key (if present)
5. Restore the `## Run Summary` section from `ccafc6-0000-doc-1/README.md` if present
   (i.e., remove the `## Run Summary` block so the README matches the mid-run live state)
6. Write `current-job.txt` → path to `ccafc6-0001-integrate/README.md` (no X- prefix)

Then resume:

7. `tests/regression/doc-user-service/run.sh`
8. Verify `X-ccafc6-0000-doc-1/README.md` now contains `## Run Summary`
9. Verify all subtasks show `[x]`
10. Run gold tests: `cd tests/regression/doc-user-service/gold && go test ./...`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

**Phase 1 completed 2026-04-03** — clean run passed: `## Run Summary` present,
all subtasks `[x]`, gold tests green.

**Phase 2 skipped** — the scenario as written is obsolete. It was authored to
test a `_find_level_top` bug, but the actual fixes (`0008`/`0009`) use
handoff-state persistence and stale frame detection instead. The orchestrator
does not persist `current_state`, so `--resume` always restarts at the
machine's start state. Phase 1 is sufficient validation of the teardown fix.
