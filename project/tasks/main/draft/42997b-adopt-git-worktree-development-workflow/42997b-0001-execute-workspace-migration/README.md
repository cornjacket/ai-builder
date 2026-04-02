# Task: execute-workspace-migration

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

Execute the workspace migration using the bootstrap scripts, verify everything
works, and complete the cutover to the new structure.

## Context

Prerequisite: `0000-implement-bootstrap-scripts` is complete and pushed to remote.

**Steps (in order):**

1. **Rename and push:** rename `ai-builder/` → `ai-builder-gold/`, write the
   bootstrap scripts (subtask `0000`) inside `ai-builder-gold/`, commit and push.

2. **Run the bootstrap procedure** (exactly as documented in `README.md`):
   ```bash
   cd ~/Go/src/github.com/cornjacket
   git clone <remote-url> ai-builder-bootstrap
   bash ai-builder-bootstrap/bootstrap/setup-workspace.sh
   rm -rf ai-builder-bootstrap
   ```
   Result: `ai-builder-gold/` (untouched), `ai-builder/` (workspace with `main/`)

3. **Verify `main/` works:**
   - Task scripts: `ai-builder/main/project/tasks/scripts/new-user-task.sh --help`
   - Orchestrator: `python3 ai-builder/main/ai-builder/orchestrator/orchestrator.py --help`
   - Regression reset (do not run the full pipeline): `bash ai-builder/main/tests/regression/user-service/reset.sh`

4. **Rename `.claude/` project memory:**
   ```bash
   mv ~/.claude/projects/-Users-david-Go-src-github-com-cornjacket-ai-builder \
      ~/.claude/projects/-Users-david-Go-src-github-com-cornjacket-ai-builder-main
   ```

5. **Copy sandbox/ from gold:**
   ```bash
   cp -r ai-builder-gold/sandbox/. ai-builder/main/sandbox/
   ```
   Critical: sandbox/ is almost entirely gitignored — brainstorms, regression
   artifacts, and all experiment outputs only exist in gold.

6. **Update CLAUDE.md** in `ai-builder/main/` to document the worktree workflow
   and update the concurrent-regression rule (safe across worktrees).

7. **Commit and push** the CLAUDE.md update from `main/`.

8. **Test new-worktree.sh**: create a throwaway worktree, verify it works,
   remove it with `remove-worktree.sh`.

9. **Mark gold as archived**: add an `ARCHIVED.md` at `ai-builder-gold/` root
   noting the date and the new workspace location.

## Notes

Do not run a full regression test during verification (step 2) — just confirm
the scripts and orchestrator are reachable and exit cleanly. Full regression
can follow in a normal session once the workspace is established.
