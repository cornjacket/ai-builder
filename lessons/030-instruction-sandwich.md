# Lesson 030 — Instruction Sandwich: Reinforce Critical Rules

**Category:** ai-collaboration
**Source project:** Cornjacket Platform
**Date:** 2026-02-13

## Context

AI instruction files are loaded at the start of a conversation. As the conversation grows, earlier instructions fade from the AI's active attention. Critical rules placed only at the beginning may silently stop being followed — a form of context rot.

## Lesson

Place critical instructions both before and after task content (the "sandwich"). Reinforce key rules through multiple surfaces: instruction files, task doc templates, agent footers, and hooks. The more important a rule, the more places it should appear. On the human side, re-state critical rules when giving complex instructions in long conversations.

## Decision Guidance

When a rule is critical (e.g., "create task doc before code changes"), don't rely on a single mention in the instruction file. Repeat it in task templates, reinforce it with hooks, and remind the agent during long sessions. If you notice a rule being violated mid-session, it's a signal to re-state it explicitly rather than assume the AI forgot on purpose.

## Related Lessons

- [019](019-instruction-file-design.md) — instruction file is one surface for rules
- [029](029-git-hooks-for-ai-compliance.md) — hooks provide deterministic reinforcement
