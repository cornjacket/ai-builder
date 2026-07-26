# Task: repo-name-rename-audit

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | LOW           |
| Category    | workspace-mgmt           |
| Created     | 2026-07-26            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Rename only the **repo self-references** (`ai-builder` → `create-ai-builder`) —
README title/clone/`cd`, and `bootstrap/setup-workspace.sh` workspace paths —
while leaving the **product/artifact** name untouched.

## Context

Re-homed from create-project-system (its placeholder task 13). The repo was
renamed `ai-builder` → `create-ai-builder`, but the string `ai-builder` still
appears **~912 times** — and **~99% must stay**: the inner `ai-builder/` engine
and every `ai-builder/orchestrator/...` path, `.gitignore` runtime entries,
regression recordings (`tests/regression/**/runs/*/execution.log`), and task
history. Those are the *product* name (the thing generated into targets), not
the repo.

**Changes:** `README.md` line 1 title, `git clone …/ai-builder.git`,
`cd ai-builder`; and `bootstrap/setup-workspace.sh` (`WORKSPACE=…/ai-builder`,
`~/.claude/projects/…cornjacket-ai-builder-*`) — **setup-critical, test after
editing** by running setup-workspace.sh in a scratch dir. **Never a repo-wide
`sed`** — go file-by-file, asking "does this name the repo, or the product?"

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
