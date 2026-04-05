# Task: add-regression-to-recordings-readme

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | f5f7b8-pipeline-acceptance-spec-writer             |
| Priority    | —           |
| Created     | 2026-04-05            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Write `tests/regression/lib/add-to-recordings-readme.sh` — a script that
adds a new row to the Regression tests table in the ai-builder-recordings
main branch README.md. Test it by adding the platform-monolith entry.

## Context

When a regression's recording is pushed to ai-builder-recordings for the
first time, the ai-builder-recordings README.md (on main branch) must be
updated to list the new branch. This step has no script and is not in the
`record-lib.sh` "Next steps" output, so it gets missed.

Branch link format: https://github.com/cornjacket/ai-builder-recordings/commits/<test-name>/

The script should:
1. Clone the ai-builder-recordings repo (main branch) to a temp dir
2. Add a row to the Regression tests table in README.md
3. Commit and push to main

After the script is written, add a "Next steps" hint to `record-lib.sh`
reminding the operator to run it when pushing a new branch for the first time.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
