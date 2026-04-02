# Bootstrap

Scripts for setting up and managing the ai-builder git worktree workspace.

See the top-level [`README.md`](../README.md) for the full bootstrap procedure.

---

## Scripts

### `setup-workspace.sh`

One-time setup. Creates the `ai-builder/` workspace with a bare clone and a
`main/` worktree. Must be run from a clone named `ai-builder-bootstrap/`.

See [`README.md`](../README.md) for the exact invocation.

### `new-worktree.sh <branch-name> [--from <base-branch>]`

Creates a new branch and worktree at `ai-builder/<branch-name>/`.
Run from inside any existing worktree (e.g., `main/`).

```bash
# Create a worktree for a new feature branch
bash bootstrap/new-worktree.sh feat-x

# Create from a specific base branch
bash bootstrap/new-worktree.sh experiment --from main
```

### `remove-worktree.sh <branch-name> [--delete-branch]`

Removes a worktree. Refuses to remove `main`. Use `--delete-branch` to also
delete the branch (safe delete — refuses if unmerged).

```bash
# Remove the worktree, keep the branch
bash bootstrap/remove-worktree.sh feat-x

# Remove the worktree and delete the branch
bash bootstrap/remove-worktree.sh feat-x --delete-branch
```

---

## Workspace structure

```
ai-builder/
    .bare/          git object store (bare clone of remote)
    .git            file: "gitdir: ./.bare"
    main/           worktree for main branch
    <branch>/       worktree for a feature branch (ephemeral)
```

## Day-to-day workflow

```bash
# Start work on a new feature
bash main/bootstrap/new-worktree.sh my-feature
cd my-feature
# ... do work, commit, push ...

# When done, merge to main and clean up
cd main
git merge my-feature
bash bootstrap/remove-worktree.sh my-feature --delete-branch
```
