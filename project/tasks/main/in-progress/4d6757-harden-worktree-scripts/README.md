# Task: harden-worktree-scripts

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | in-progress             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | bootstrap              |
| Created     | 2026-04-05            |
| Completed   | —                      |
| Next-subtask-id | 0003 |

## Goal

Harden `new-workflow.sh`, `new-worktree.sh`, and `remove-worktree.sh` with three
improvements:

1. **Main-worktree guard** — abort if the script is not being run from the `main`
   worktree. Feature-branch worktrees should never drive workflow operations.
2. **Fetch before acting** — run `git fetch --prune origin` at the start of each
   script so remote state is current before any decision is made.
3. **Atomic remove in `remove-worktree.sh`** — remove the `--delete-branch` flag;
   always delete the worktree directory AND its branch together. Before deleting,
   check whether the branch is merged using `gh pr list --state merged --head
   <branch>` (reliable for squash/rebase PRs) with `origin/<branch>` absence
   (after prune) as a fallback. Refuse if the branch does not appear merged.

Also document the main-worktree requirement in `bootstrap/README.md` and `CLAUDE.md`.

## Context

`remove-worktree.sh` previously required `--delete-branch` to delete the branch,
meaning deleting the worktree without the flag left an orphaned local branch.
This caused confusion (acceptance-spec worktree was removed but branch remained).

The `git branch -d` safe-delete does not work for squash/rebase PR merges because
the squashed commit is not an ancestor of the feature branch tip. The fix is to
check merge status via `gh pr list --state merged` and/or remote branch absence
after `git fetch --prune`.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-4d6757-0000-add-main-worktree-guard-and-fetch](X-4d6757-0000-add-main-worktree-guard-and-fetch/)
- [x] [X-4d6757-0001-make-remove-worktree-atomic](X-4d6757-0001-make-remove-worktree-atomic/)
- [x] [X-4d6757-0002-update-docs](X-4d6757-0002-update-docs/)
<!-- subtask-list-end -->

## Notes

_None._
