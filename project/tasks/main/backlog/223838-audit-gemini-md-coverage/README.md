# Task: audit-gemini-md-coverage

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | docs                   |
| Created     | 2026-04-04            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Ensure every committed `CLAUDE.md` in the repo has a corresponding `GEMINI.md`
symlink in the same directory (`GEMINI.md -> CLAUDE.md`). Add a rule to the
root `CLAUDE.md` requiring this pairing for any new `CLAUDE.md` going forward.

## Context

`GEMINI.md` is always a symlink to `CLAUDE.md` — not a separate file. This
guarantees they are always identical with no sync burden. `target/init-claude-md.sh`
already creates the symlink for generated target repos.

**Completed (2026-04-04):** The two committed pairs have been converted to symlinks:

- `GEMINI.md -> CLAUDE.md` (repo root)
- `tests/regression/GEMINI.md -> CLAUDE.md`

**Remaining work:**

1. **Coverage rule** — add a rule to the root `CLAUDE.md`: whenever a new
   `CLAUDE.md` is created, create `GEMINI.md` as a symlink to it in the same
   commit (`ln -s CLAUDE.md GEMINI.md`).

2. **Audit any new CLAUDE.md locations** — if new `CLAUDE.md` files are added
   in future worktrees or subdirectories, verify the symlink exists.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

`target/init-claude-md.sh` already handles symlink creation for regression
target repos — no change needed there.
