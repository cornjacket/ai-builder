# Task: add-claude-md-work-log-rule

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 14fb29-add-work-log-mechanism             |
| Priority    | —           |
| Created     | 2026-04-30            |
| Completed | 2026-04-30 |
| Next-subtask-id | 0000               |

## Goal

Add a new `## Work Log` section to `CLAUDE.md` (between `## Git Commits` and
`## Brainstorming`) containing a `> **Rule:**` block that enforces the
work-log convention. Add a one-line cross-reference in the Git Commits section.

## Context

The rule must call out both failure modes (entries-per-prompt and
tasks-without-entries), require the short commit hash on every entry, and
forbid dedicated back-fill commits. It must reference the helper script
introduced in 0002 and link to lesson 038 for the rationale.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
