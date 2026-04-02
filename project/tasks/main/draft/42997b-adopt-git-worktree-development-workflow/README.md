# Task: adopt-git-worktree-development-workflow

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | draft             |
| Epic        | main               |
| Tags        | —               |
| Priority    | HIGH           |
| Created     | 2026-04-02            |
| Completed   | —                      |
| Next-subtask-id | 0002 |

## Goal

Adopt a git worktree development workflow for the ai-builder repo, enabling
parallel work on multiple branches simultaneously without stashing or context
switching. Each branch lives in its own sibling directory; `main` is one of them.

## Context

Currently the repo lives at a single path (`ai-builder/`) on a single branch
at a time. Feature work, experiments, and fixes all compete for the same working
tree. Git worktrees solve this: `git worktree add` creates a linked working
directory on a separate branch, sharing the same `.git` object store with zero
clone overhead.

**Preferred structure:**

```
ai-builder.git/      ← bare repo (object store, no working tree) — OR —
ai-builder-main/     ← worktree for 'main'
ai-builder-feat-x/   ← worktree for a feature branch (ephemeral)
```

The base/bare-clone approach is the end-state; the non-bare approach (rename
current dir to `ai-builder-main`, add worktrees as siblings) is the pragmatic
first step. See brainstorm for full analysis.

**Impact summary (from brainstorm analysis):**
- Task scripts: safe — REPO_ROOT derived relative to script location ✓
- Orchestrator: safe — REPO_ROOT derived relative to `.py` file location ✓
- Regression tests: safe + improved — each worktree gets its own sandbox ✓
- Go modules: safe — module path is independent of directory name ✓
- `.claude/` project memory: path changes on rename; new worktrees get separate memory (fine) ✓

**Brainstorm:** `sandbox/brainstorms/brainstorm-git-worktree-development-workflow.md`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [ ] [42997b-0000-implement-bootstrap-scripts](42997b-0000-implement-bootstrap-scripts/)
- [ ] [42997b-0001-execute-workspace-migration](42997b-0001-execute-workspace-migration/)
<!-- subtask-list-end -->

## Notes

Design decisions (see brainstorm for full analysis):
- Existing `ai-builder/` renamed to `ai-builder-gold/` — never touched again
- New `ai-builder/` is a plain workspace container, not a git repo
- Bare clone from remote (not from gold) is the object store
- Worktrees are ephemeral (created per task, deleted on merge)
- `sandbox/` must be copied from gold — it is gitignored and won't be in the clone
