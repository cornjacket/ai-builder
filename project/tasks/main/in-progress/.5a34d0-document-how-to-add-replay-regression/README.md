# Task: document-how-to-add-replay-regression

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | in-progress             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Created     | 2026-04-03            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Add a section to `tests/regression/how-to-write-a-regression-test.md`
covering how to set up replay regression support for a new test. The guide
currently covers only live runs. The new section should cover:

1. **When to add replay** — criteria for deciding if a test warrants it
   (test is stable, exercises meaningful routing, high re-run frequency)
2. **The recordings remote** — `cornjacket/ai-builder-recordings`, one
   orphan branch per test, naming convention (branch name = test name)
3. **`record.sh` structure** — what the script must do (reset, run
   orchestrator with `--record-to`/`--record-branch`/`--record-remote`,
   push with `--force`); use `user-service/record.sh` as the template
4. **`test-replay.sh` structure** — what the script must do (fetch if
   absent, reset with pinned task ID, replay with `--replay-from`, verify
   routing, compare snapshot); use `user-service/test-replay.sh` as the
   template
5. **Taking the first recording** — the initial live `record.sh` run that
   establishes the baseline; confirm with one `test-replay.sh` pass before
   treating it as golden
6. **Refreshing a recording** — when and how (prompt drift, behaviour
   change, `record.sh --force`)

## Context

`tests/regression/how-to-write-a-regression-test.md` is the authoritative
guide for adding regression tests. Replay support is entirely absent from
it. The `user-service` test is the reference implementation — both
`record.sh` and `test-replay.sh` there serve as templates. The guide
should link to them and to `ai-builder/orchestrator/record-replay.md` for
the orchestrator-level reference.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
