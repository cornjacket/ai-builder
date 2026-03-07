# Lesson 029 — Git Hooks for AI Compliance

**Category:** tooling
**Source project:** Cornjacket Platform
**Date:** 2026-02-13

## Context

AI agent instructions rely on the agent voluntarily following rules. As conversations grow longer, earlier instructions fade from attention ("context rot"). Rules like "always create a task doc before code changes" can silently stop being followed mid-session.

## Lesson

Use git hooks (pre-commit, pre-push) to enforce critical rules deterministically. Hooks cannot be bypassed by attention dilution — they run regardless of what the agent remembers. Version-control the hooks in a shared location and install them via bootstrap scripts. Start with the highest-value checks: task doc exists alongside code changes, doc size warnings, and sandbox content rejection.

## Decision Guidance

When a rule is critical enough to never be skipped, enforce it with a hook rather than an instruction. Instructions are suggestions; hooks are guardrails. Start advisory (warn but allow) and move to strict (reject) once the team is comfortable. Keep hooks fast — slow hooks get bypassed with `--no-verify`.

## Related Lessons

- [003](003-every-change-needs-a-task-document.md) — first candidate for hook enforcement
- [015](015-bootstrap-scripts-for-multi-repo-workspaces.md) — bootstrap installs hooks
