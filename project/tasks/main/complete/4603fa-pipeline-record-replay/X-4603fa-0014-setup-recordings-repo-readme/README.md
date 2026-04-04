# Task: setup-recordings-repo-readme

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 4603fa-pipeline-record-replay             |
| Priority    | —           |
| Created     | 2026-04-03            |
| Completed | 2026-04-03 |
| Next-subtask-id | 0000               |

## Goal

Create `README.md` on the `main` branch of `cornjacket/ai-builder-recordings`
that explains the repo, its structure, and how to use it. The README must:

1. **Describe the repo** — what it is (recording storage for ai-builder
   replay regression tests), what the branches represent (one orphan branch
   per regression test, branch name = test name), and that history is replaced
   on every re-record (no historical runs are retained)
2. **List all current regression branches** — a table with test name, branch
   link (linking to the branch's commit list on GitHub using the URL format
   `https://github.com/cornjacket/ai-builder-recordings/commits/<test-name>/`),
   and a short description of what the test exercises; update this table
   whenever a new replay regression is added
3. **How to read a recording** — commit log format (`inv-NN ROLE OUTCOME`),
   what `recording.json` contains, where response files live
4. **Instructions for Claude** — when adding a new replay regression: create
   a new orphan branch named after the test, push the initial recording, add a
   row to the README table; when re-recording: wipe local `.git`, re-record,
   force-push (history is replaced, README table entry is unchanged)

Also update `tests/regression/user-service/record.sh` to push a README update
to `ai-builder-recordings` main branch after each re-record (or provide a
standalone `bootstrap/update-recordings-readme.sh` script that can be run
after adding a new regression test).

## Context

`cornjacket/ai-builder-recordings` currently has no README — it is opaque
to anyone (or any AI) who opens it. The branch-per-test convention and the
stacked-runs-replaced-on-rerecord policy exist only in the orchestrator
documentation, not in the repo itself. A README on `main` is the right home
for this since `main` is the natural landing branch when cloning or browsing.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
