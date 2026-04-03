# Task: document-how-to-add-replay-regression

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 4603fa-pipeline-record-replay             |
| Priority    | —           |
| Created     | 2026-04-03            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Three deliverables:

### 1. Fix `record.sh` — wipe recording history on re-record

`record.sh` must delete the recording repo's `.git` directory before each
run so that re-recording always starts with a clean history. Currently
`recorder.init()` returns early if `.git` exists, causing new runs to
append on top of old ones. This produces confusing duplicate invocation
numbers in the git log. Old recordings are never replayed once superseded,
so there is no reason to retain them.

Fix: add `rm -rf "$RECORD_DIR/.git"` at the start of `record.sh` (before
calling the orchestrator). The subsequent `recorder.init()` will
reinitialize from scratch, and `--force` push will replace the remote
branch cleanly.

### 2. Section in `how-to-write-a-regression-test.md`

Add a "Adding Replay Support" section covering:

1. **When to add replay** — test is stable, exercises meaningful routing,
   high re-run frequency
2. **The recordings remote** — `cornjacket/ai-builder-recordings`, one
   orphan branch per test (branch name = test name); see `ai-builder-recordings/README.md`
3. **`record.sh` structure** — reset, run orchestrator with
   `--record-to`/`--record-branch`/`--record-remote`, wipe `.git` before
   recording, push with `--force`; use `user-service/record.sh` as template
4. **`test-replay.sh` structure** — fetch if absent, reset with pinned task
   ID, replay with `--replay-from`, verify routing, compare snapshot; use
   `user-service/test-replay.sh` as template
5. **Taking the first recording** — initial live `record.sh` run; confirm
   with one `test-replay.sh` pass before treating as golden
6. **Refreshing a recording** — when and how: prompt drift, behaviour
   change, `record.sh --force`; re-recording replaces history entirely

### 3. README for `cornjacket/ai-builder-recordings`

Covered by subtask `4603fa-0014-setup-recordings-repo-readme` (see below).

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
