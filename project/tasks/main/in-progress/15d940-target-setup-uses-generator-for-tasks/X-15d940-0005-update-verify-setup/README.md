# Task: update-verify-setup

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 15d940-target-setup-uses-generator-for-tasks             |
| Priority    | —           |
| Created     | 2026-07-28            |
| Completed | 2026-08-03 |
| Next-subtask-id | 0000               |

## Goal

Rewrite `verify-setup.sh` so it checks what a target install is now, grouped by
the two layers, and actually fails when a layer is broken.

## Context

It was stale **before this branch**, not because of it: it grepped
`task-management-start` (a sentinel the retired `init-claude-md.sh` wrote) and
required `task-template.md`, a file that has not existed for some time. It was
also flat — a list of paths with no notion of which layer owned what.

Restructured into four groups:

- **Layer 1 — from the pinned generator:** structure (scripts, docs, status,
  the six epic folders), machinery scripts and their executability,
  `task-config.sh` / `task-env.sh` (the decoupled-path config that lets the
  scripts run from a non-default mount), templates, `docs/{USING,README,
  task-manager}.md`, and `.claude/skills/task-system/SKILL.md`.
- **Layer 2 — the overlay:** the 7 pipeline scripts, present and executable,
  from an array kept in step with `setup-project.sh`.
- **Layer 2 negative:** `ai-builder/`, `tasks/machines/` and `tasks/roles/`
  must be **absent**. This turns the thin-target decision from 0002 into an
  enforced invariant rather than a comment — if someone later "helpfully"
  copies the engine into targets, this fails.
- **Conventions:** `CLAUDE.md` present and containing exactly one
  `task-system:begin` block, `GEMINI.md` a symlink resolving to `CLAUDE.md`.

Sentinel updated `task-management-start` → `task-system:begin`, and the
`task-template.md` check dropped.

**Verified both directions.** Against a good install: 60 passed, 0 failed.
Against a copy with four deliberate breakages — a deleted pipeline script, a
deleted layer-1 doc, an `ai-builder/` directory planted in the target, and
`GEMINI.md` replaced by a regular file — it reported 6 failures spanning all
four check families and exited 1. A verifier that only ever passes is worth
nothing, so the negative case is the one that mattered.

This should also unblock section 5 of
`tests/regression/template-setup/test.sh`, which invokes this script; the
suite itself still needs explicit approval to run (subtask 0006).

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
