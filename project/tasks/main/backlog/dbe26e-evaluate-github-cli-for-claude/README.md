# Task: evaluate-github-cli-for-claude

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | workspace-mgmt         |
| Created     | 2026-04-04            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Decide whether to install and configure the GitHub CLI (`gh`) as an available
tool for Claude Code sessions in this workspace, and if so, what permissions
and configuration it requires.

## Context

Claude Code can invoke `gh` via Bash to interact with GitHub: creating and
reviewing PRs, checking CI status, managing issues, browsing workflow runs,
and merging branches. This would be directly useful for the regression manager
session concept (`15bff5-regression-manager-session`), where the overlord
Claude is expected to push branches, monitor CI, and merge approved PRs.

**Questions to resolve:**

1. **Is `gh` already installed?** Check `which gh` and `gh --version`.
2. **Is it authenticated?** `gh auth status` — if not, what auth flow is
   appropriate for a CLI tool used by an AI session?
3. **What permissions are needed?** At minimum: `repo` scope for PR creation
   and merge, `actions` scope for CI status. Determine whether a fine-grained
   token or OAuth app is more appropriate.
4. **Are there safety concerns?** `gh pr merge` and `gh repo delete` are
   destructive. Evaluate whether Claude should be allowed to run these
   unilaterally or only with explicit per-invocation user approval (the
   existing CLAUDE.md risky-action rules already require confirmation for
   pushes and merges).
5. **Scope of use:** Should `gh` be available to all Claude sessions (main,
   feature worktrees, regression manager) or only to the regression manager?

**Expected output:** A short decision document and, if approved, the
installation/auth steps recorded in `bootstrap/` or the workspace CLAUDE.md.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
