# Task: add-recordings-status-check-script

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | ccf4a4-establish-regression-recordings             |
| Priority    | —           |
| Created     | 2026-04-05            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Write `tests/regression/check-recordings-status.sh` — a script that cross-references
all full-pipeline regression directories against remote branches in `ai-builder-recordings`
(via `gh api`) and reports which regressions have/don't have a recording.

## Context

We have no local clone of ai-builder-recordings and no easy way to determine recording
status without reasoning from memory. `gh api repos/cornjacket/ai-builder-recordings/branches`
gives us the branch list without needing a local clone.

**The script should:**
1. Query remote branches via `gh api repos/cornjacket/ai-builder-recordings/branches --jq '.[].name'`
2. Walk `tests/regression/` to find all regressions that have a `run.sh` (i.e. are full-pipeline, not excluded)
3. For each, report: recorded ✓ or missing ✗
4. Exit non-zero if any recordings are missing (useful for CI)

**Exclusions:** `infra-smoke`, `goldutil`, `lib` — same as the ccf4a4 task parent.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
