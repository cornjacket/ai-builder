# Task: document-installation-dependencies

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | docs                   |
| Created     | 2026-04-05            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Audit all external dependencies required to run ai-builder and document them in
the public-facing installation docs (README.md and/or a dedicated prerequisites
section). Each dependency should include: what it is, why it is needed, and how
to install it.

Known dependencies to document:
- `gh` (GitHub CLI) — required by `remove-worktree.sh` for reliable merge
  detection after squash/rebase PRs; install via `brew install gh` + `gh auth login`
- `python3` — orchestrator runtime
- Any other tools surfaced during the audit (e.g. `go`, `git`, `jq`)

## Context

`remove-worktree.sh` uses `gh pr list --state merged` as its primary merge check.
Without `gh`, it falls back to inferring merge from remote branch absence, which
is less reliable. Users who hit this gap need clear installation guidance.

The broader gap is that the repo has no single place that lists what a new
contributor needs installed before they can use ai-builder.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
