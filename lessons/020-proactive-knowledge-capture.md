# Lesson 020 — Proactive Knowledge Capture During AI Sessions

**Category:** process
**Source project:** Cornjacket Platform
**Date:** 2026-02-13

## Context

Knowledge extraction from AI sessions typically only happens when the human explicitly asks. But valuable insights, patterns, process gaps, and reusable knowledge emerge organically during normal work — and are lost when the conversation ends.

## Lesson

Instruct AI agents to proactively flag knowledge worth capturing during any work session. This includes: patterns worth repeating, anti-patterns encountered, process gaps discovered, library quirks, architectural observations, and repeatable manual steps that should be scripted. The agent should note these in a designated location (outbox, sandbox, or backlog) for later triage — not interrupt the current task.

## Decision Guidance

When setting up AI agent instructions, include a standing order to capture knowledge proactively. Define where observations go (a scratch file, outbox, or backlog item) and who triages them. The cost of a brief note is negligible; the cost of rediscovering a lost insight is high.

## Related Lessons

- [001](001-separate-meta-learning-from-project-repos.md) — captured knowledge may belong in a meta-learning repo
- [002](002-project-insights-folder-complements-adrs.md) — project insights as a destination for captured knowledge
