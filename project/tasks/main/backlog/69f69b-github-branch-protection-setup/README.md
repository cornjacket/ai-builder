# Task: github-branch-protection-setup

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | HIGH           |
| Category    | workspace-mgmt         |
| Created     | 2026-04-02            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Configure GitHub branch protection on `main` to reject direct pushes and
require PRs with passing CI before merging.

## Context

Once the CI workflow (`f00df6-0005`) is live and has run at least once,
GitHub will know the `unit-tests` job name and it can be added as a required
status check.

**Do not enable until all active work on `main` is complete** — branch
protection will block direct pushes immediately.

## Steps

1. Go to: `github.com/cornjacket/ai-builder → Settings → Branches`
2. Click **Add branch ruleset**
3. Configure:
   - **Target branch:** `main`
   - **Require a pull request before merging:** ✅ (blocks direct pushes)
   - **Require status checks to pass:** ✅
     - Add check: `unit-tests` (the job name from `.github/workflows/unit-tests.yml`)
   - **Block force pushes:** ✅
   - **Do not allow bypasses:** ✅ (includes repo admins)
4. Save

## Notes

- Prerequisite: `f00df6-0005` (CI workflow) must be merged and have at least
  one successful run so GitHub recognises the `unit-tests` check name.
- After enabling, all work must go through PRs. Create a worktree for each
  task (`bootstrap/new-worktree.sh`) and open a PR from the feature branch.
