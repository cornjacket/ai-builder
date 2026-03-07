# Lesson 025 — Use a Sandbox for Throwaway Experiments

**Category:** process
**Source project:** Cornjacket Platform
**Date:** 2026-02-13

## Context

AI agents need a place to write dirty code, test assumptions, brainstorm designs, and verify library behavior without polluting the codebase. Without a designated playground, experiments either end up in production code or don't happen at all.

## Lesson

Create a gitignored sandbox directory for throwaway work: brainstorming docs, code spikes, library experiments, design explorations. Give each agent role its own subfolder to prevent collisions. Define a clear lifecycle: create → work → extract valuable content to proper locations → clean up. The sandbox must never be used for task implementation — it bypasses traceability.

## Decision Guidance

When setting up a project, create the sandbox early. Define rules: nothing permanent lives there, valuable discoveries get extracted to version-controlled locations, and the sandbox is never a substitute for proper task documents. Per-agent subfolders scale better than a flat directory as the team grows.

## Related Lessons

- [001](001-separate-meta-learning-from-project-repos.md) — extracted sandbox content may become lessons
- [003](003-every-change-needs-a-task-document.md) — sandbox doesn't replace task docs
