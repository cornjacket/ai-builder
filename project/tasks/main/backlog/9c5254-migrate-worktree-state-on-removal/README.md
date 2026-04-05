# Task: migrate-worktree-state-on-removal

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | bootstrap              |
| Created     | 2026-04-05            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Before `remove-worktree.sh` deletes a worktree, scan for worktree-specific
state that would be silently lost and either migrate it to the main worktree
or block removal with a clear message listing what needs to be resolved first.

State to check:

1. **Claude memory files** — Claude Code stores per-project memories keyed to
   the working directory path. A worktree at `ai-builder/<branch>/` has a
   distinct memory path from `ai-builder/main/`. Any memory files written
   during work in the worktree will not be visible from `main/` after deletion.
   The script should detect whether a memory directory exists for the worktree
   path, report its contents, and copy files into the main worktree's memory
   directory (merging `MEMORY.md` index entries).

2. **Uncommitted sandbox state** — `sandbox/` is gitignored. Any files written
   there (brainstorms, experiment output, etc.) are lost on worktree removal.
   Flag if `sandbox/` contains anything beyond the standard gitignored
   regression artefact dirs (`sandbox/regressions/`).

3. **Session status logs** — `project/status/` files are tracked in git, so
   they survive removal only if committed. Flag any untracked or modified
   status files.

Removal should be blocked (or require explicit acknowledgement) if unresolved
state is found. The goal is that no information silently disappears when a
worktree is removed.

## Context

When the `acceptance-spec` worktree was deleted, any Claude memories written
during that session were keyed to the acceptance-spec worktree path and did not
automatically carry over to `main/`. The same risk applies to any worktree.
Claude memory paths are based on the project directory, so
`ai-builder/acceptance-spec/` and `ai-builder/main/` are distinct memory
namespaces.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
