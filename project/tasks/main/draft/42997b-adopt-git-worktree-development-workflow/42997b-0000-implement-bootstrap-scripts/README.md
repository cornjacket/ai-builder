# Task: implement-bootstrap-scripts

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 42997b-adopt-git-worktree-development-workflow             |
| Priority    | HIGH           |
| Created     | 2026-04-02            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Write and commit the three bootstrap scripts that build the git worktree
workspace structure, then push to remote so they are available in the clone.

## Context

These scripts are the only permitted mechanism for setting up the workspace.
No manual git operations during migration — the scripts must be self-contained
and testable. They live in `bootstrap/` in the repo root.

**Scripts to implement:**

**`bootstrap/setup-workspace.sh`** — one-time migration, run from `cornjacket/`:
1. Validate: `ai-builder/` exists and has a remote origin URL; warn if unpushed commits
2. Read remote URL from `ai-builder/.git/config`
3. Rename `ai-builder/` → `ai-builder-gold/`
4. `mkdir ai-builder/`
5. `git clone --bare <remote-url> ai-builder/.bare`
6. `echo "gitdir: ./.bare" > ai-builder/.git`
7. Fix fetch refspec: `git -C ai-builder/.bare config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"`
8. `git -C ai-builder worktree add main main`
9. Print success + instructions for sandbox copy and memory rename

**`bootstrap/new-worktree.sh <branch-name> [--from <base>]`** — run from `ai-builder/`:
1. Validate branch name not already in use
2. `git worktree add <branch-name> -b <branch-name> <base>`
3. Print path and next steps

**`bootstrap/remove-worktree.sh <branch-name> [--delete-branch]`** — run from `ai-builder/`:
1. Validate: exists, is not `main`
2. `git worktree remove <branch-name>`
3. If `--delete-branch`: `git branch -d <branch-name>` (safe, refuses if unmerged)

**`bootstrap/README.md`** — documents all three scripts, the workspace structure,
and the day-to-day worktree workflow.

After implementing, commit and push to remote before starting `0001`.

## Notes

See brainstorm: `sandbox/brainstorms/brainstorm-git-worktree-development-workflow.md`
