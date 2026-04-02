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

**`bootstrap/setup-workspace.sh`** — run from inside the ai-builder repo root.
Bash holds the file open so execution continues after the directory is renamed.
1. Validate: inside a git repo with a remote origin URL; abort if unpushed commits
2. Read remote URL from `.git/config`
3. Rename `../ai-builder/` → `../ai-builder-gold/`
4. `mkdir ../ai-builder/`
5. `git clone --bare ../ai-builder-gold/ ../ai-builder/.bare/`  ← local clone, fast
6. `git -C ../ai-builder/.bare remote set-url origin <remote-url>`  ← reconfigure remote
7. `echo "gitdir: ./.bare" > ../ai-builder/.git`
8. Fix fetch refspec
9. `git -C ../ai-builder worktree add main main`
10. Print success + instructions for sandbox copy and memory rename

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

**Top-level `README.md`** — add a "Getting Started" section explaining how to
bootstrap the workspace on a fresh machine:
```
git clone <remote-url> ai-builder-setup
cd ai-builder-setup
bash bootstrap/setup-workspace.sh
rm -rf ../ai-builder-setup
```
This must be in the README so it's visible on GitHub before the workspace exists.

After implementing all of the above, commit and push to remote before starting `0001`.

## Notes

See brainstorm: `sandbox/brainstorms/brainstorm-git-worktree-development-workflow.md`
