# Task: regression-manager-session

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | draft             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Created     | 2026-04-03            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Design and implement a dedicated regression manager: a Claude session
invoked from the workspace root that owns regression runs across all
active worktrees, coordinating execution and updating task status without
conflicting with feature development sessions.

## Context

**The problem today:**
Each worktree session (Claude Code) is responsible for running its own
regressions. This creates two issues:
1. Regressions are long-running and tie up the development session
2. Each session must independently track regression state, approve runs,
   and update task status — there is no single view of what is passing or
   failing across worktrees

**The proposed solution:**
A dedicated Claude session invoked from the workspace root (`ai-builder/`)
— the parent directory above all worktrees — that is responsible solely for
running regressions and updating task status. Feature development sessions
delegate regression work to this manager rather than running regressions
themselves.

**Design options — needs brainstorm:**

**Option A — Orphan branch**
A branch with no history that contains only the regression infrastructure
(reset.sh, run.sh, gold tests, orchestrator). Not derived from main. Shared
sandbox is its working area. Lightweight; no merge concerns with feature
branches. Con: must manually sync pipeline changes from main when the
orchestrator changes.

**Option B — Long-lived tracking branch**
A branch that regularly merges or rebases from main, keeping the full
codebase in sync. Regressions always run against the latest orchestrator.
A worktree is created for this branch at the workspace root level (e.g.
`ai-builder/regression/`). The Claude session in that worktree runs
regressions on demand, reads task READMEs from feature worktrees to find
pending regression subtasks, and writes results back.

**Option C — Rootless session (no worktree)**
Claude Code invoked from `ai-builder/` (the workspace root itself, which
is not a git worktree). Has read access to all sibling worktrees via the
filesystem. Runs regressions by shelling into the appropriate worktree.
Updates task status by directly editing files in the target worktree.
Avoids any branch management entirely.

**Cross-worktree communication:**
Regardless of option, the manager needs to:
- Discover which worktrees have pending regression subtasks
- Know which regression suite to run for each
- Write results back into the correct worktree's task README
- Not conflict with the development session editing files in the same worktree

**Key questions for brainstorm:**
- How does the regression manager discover pending regression subtasks
  across worktrees? (scan task dirs? a shared queue file? explicit
  invocation from the dev session?)
- Can two Claude sessions safely write to different files in the same
  worktree simultaneously?
- Is Option C (rootless) viable — does Claude Code work correctly when
  invoked from a directory that is not itself a git worktree?
- Should the regression manager push results to a shared branch, or write
  directly to each worktree's files?
- How does approval work — does the user approve in the regression session
  or delegate approval from the dev session?

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
