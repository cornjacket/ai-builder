# Task: design-cross-worktree-memory-sync

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | draft             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | workspace-mgmt         |
| Created     | 2026-04-03            |
| Completed   | —                      |
| Next-subtask-id | 0005 |

## Goal

Design and implement a memory sync system so that Claude Code memories are
shared correctly across worktree branches:

1. **Propagate main → new worktree on creation** — when `new-worktree.sh`
   creates a branch, copy `main/` memories into the new worktree's memory
   directory so it starts with full context.
2. **Propagate worktree → main on merge** — when a worktree is removed
   (merged), new or updated memories from that worktree should be merged back
   to `main/` memories.
3. **Common deletion** — when a memory is deleted in one worktree, propagate
   the deletion to main and sibling worktrees.
4. **Scripts to manage this** — `sync-memories-to-main.sh`,
   `sync-memories-from-main.sh` (or similar), called by `new-worktree.sh`
   and `remove-worktree.sh`.
5. **Investigate Gemini memory model** — how does Gemini/Google AI handle
   memory across sessions? Are there patterns worth borrowing? (Lower priority
   now that Claude Code can run with Gemini models via `--model` flag.)

## Context

Claude Code stores memories per working directory path under
`~/.claude/projects/<path-slug>/memory/`. Each worktree maps to a different
path slug, so memories written in `pipeline-record-replay/` are invisible to
sessions in `main/` or any other worktree.

This means feedback, project context, and behavioral rules written during a
feature branch session are silently lost when the worktree is deleted, and
are also invisible to other concurrent worktrees. The current workaround is
to write behavioral rules to `CLAUDE.md` instead of memory — but that is
a blunt instrument that forces everything into the committed file.

The ideal state: `main/` memory is the canonical store; worktree memories
are derived from it on creation and merged back on teardown.

Memory directory path format: `~/.claude/projects/-Users-david-Go-src-github-com-cornjacket-ai-builder-<branch>/memory/`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [ ] [b4d83d-0000-investigate-gemini-memory-model](b4d83d-0000-investigate-gemini-memory-model/)
- [ ] [b4d83d-0001-design-sync-protocol](b4d83d-0001-design-sync-protocol/)
- [ ] [b4d83d-0002-implement-sync-scripts](b4d83d-0002-implement-sync-scripts/)
- [ ] [b4d83d-0003-update-worktree-scripts-to-call-sync](b4d83d-0003-update-worktree-scripts-to-call-sync/)
- [ ] [b4d83d-0004-document-memory-sync-system](b4d83d-0004-document-memory-sync-system/)
<!-- subtask-list-end -->

## Notes

_None._
