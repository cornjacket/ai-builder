# Task: post-push-ci-check

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | HIGH           |
| Category    | task-tooling           |
| Created     | 2026-04-30            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

After every `git push` to `main` (and ideally feature branches too),
automatically check the resulting GitHub Actions run via `gh run` and surface
failures back to the operator before any further work proceeds.

## Context

We pushed `9381b23` on 2026-04-30 and only noticed the unit-tests workflow
had failed two prompts later, when the user asked. Main was red for ~1.5h
and a follow-up commit (`fd5c9ce`) was needed to repair it. The underlying
gap: there is no enforced post-push step that polls `gh run` and reports
the result back to the AI/human operator.

**Proposed behaviour:**
- A helper script `project/scripts/check-ci.sh` that:
  - Resolves the most recent run for the current branch+commit via
    `gh run list --branch <branch> --commit <sha>` or `gh run watch`.
  - Polls until the run completes (or returns immediately if already done).
  - Exits non-zero on failure, prints a one-line summary on success.
- Optionally invoked automatically from a git `post-push` hook, or from
  `bootstrap/new-workflow.sh` / `bootstrap/remove-worktree.sh` so worktree
  removal is blocked when CI is red.
- Documented in `CLAUDE.md` so the AI operator knows to run it (or that the
  hook is wired up) after every push.

**Adjacent work:**
- `69f69b-github-branch-protection-setup` (HIGH, backlog) — would prevent
  red main via required-checks branch protection. That is the *prevention*;
  this task is the *detection* layer for the AI/human operator.

**Out of scope:** turning this into a Claude Code Stop/PostToolUse hook
(different mechanism — `update-config` skill territory).

## Subtasks

(To be designed when this task is picked up. Likely: write the script,
write its companion `.md`, decide where it gets invoked from, update
CLAUDE.md, add a final docs subtask.)

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
