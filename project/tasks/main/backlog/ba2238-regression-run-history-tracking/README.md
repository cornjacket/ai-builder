# Task: regression-run-history-tracking

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | regression-infra       |
| Next-subtask-id | 0000               |

## Goal

Every regression test should have `claude-run-history.md` and
`gemini-run-history.md` files under a `results/` directory. Each run row
must include a `Notes` column that references the task/subtask that
triggered the run. The `how-to-write-a-regression-test.md` guide must be
updated to include creating these files as a required step.

Confirm whether the pipeline itself (or a wrapper script) can append a row
to the run-history deterministically at the end of each run, so manual
entry is not required.

## Context

Currently only the fibonacci regression has `results/gemini-run-history.md`
(created ad hoc). Platform-monolith and user-service have no run-history
files — their data is scattered across the now-closed brainstorm task.

Without task references in run notes it is impossible to reconstruct why a
run was done or what optimization it was validating. For example, run 14
(platform-monolith, 2026-03-21) validated DECOMPOSE_HANDLER internalization
from `829461-split-task-format-and-internalize-decompose-handler` — that
link doesn't exist anywhere today.

**Required per regression:**
- `tests/regression/<name>/results/claude-run-history.md`
- `tests/regression/<name>/results/gemini-run-history.md`

**Required columns:** Run, Date, State machine, Elapsed, Tokens out,
Tokens cached, Resumed, Gold, Notes (task/subtask reference + one-line
context).

**Determinism question:** Investigate whether `run-metrics.json` (already
written at end of each run) could drive an automatic row append to the
appropriate run-history file. If the pipeline can determine the agent type
(claude vs gemini) from the machine file, it could write the row itself.
If not, document the manual process clearly in `how-to-write-a-regression-test.md`.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
