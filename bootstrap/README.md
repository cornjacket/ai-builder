# Bootstrap

Scripts for setting up and managing the ai-builder git worktree workspace.

See the top-level [`README.md`](../README.md) for the full bootstrap procedure.

> **Rule:** `new-workflow.sh`, `new-worktree.sh`, and `remove-worktree.sh` must
> always be run from the **main worktree** (`ai-builder/main/`). Each script
> enforces this with a guard and fetches remote state before taking any action.

---

## Scripts

### `setup-workspace.sh`

One-time setup. Creates the `ai-builder/` workspace with a bare clone and a
`main/` worktree. Must be run from a clone named `ai-builder-bootstrap/`.

See [`README.md`](../README.md) for the exact invocation.

### `new-workflow.sh -taskname <task-name> -name <worktree-name> [-epic <epic>]`

The standard entry point for starting work on a task. Run from `main/`.

1. Locates the task in `draft/`, `backlog/`, or `in-progress/`
2. Moves it to `in-progress/` and commits (skips if already there)
3. Creates a new worktree branched from the current `main` HEAD
4. Prints next steps

```bash
bash bootstrap/new-workflow.sh \
    -taskname f5f7b8-pipeline-acceptance-spec-writer \
    -name     acceptance-spec
```

### `new-worktree.sh <branch-name> [--from <base-branch>]`

Low-level primitive — creates a branch and worktree only. Prefer
`new-workflow.sh` for task-tracked work; use this directly for
experiments or branches not tied to a task.

```bash
bash bootstrap/new-worktree.sh feat-x
bash bootstrap/new-worktree.sh experiment --from main
```

### `remove-worktree.sh <branch-name>`

Removes a worktree and its branch atomically. Refuses to remove `main` or any
branch that does not have a confirmed merged PR. Uses `gh pr list --state merged`
as the primary merge check (reliable for squash/rebase PRs), with remote branch
absence as a fallback when `gh` is unavailable.

```bash
bash bootstrap/remove-worktree.sh feat-x
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

All commands run from `ai-builder/main/`.

```bash
# Start work on a task (moves task to in-progress, commits, creates worktree)
bash bootstrap/new-workflow.sh -taskname <hex-id>-<task-name> -name <worktree-name>

# Open a new session in the worktree and do the work

# When done, open a PR on GitHub and merge it

# Remove the worktree (verifies merged via gh before deleting)
bash bootstrap/remove-worktree.sh <worktree-name>
```
