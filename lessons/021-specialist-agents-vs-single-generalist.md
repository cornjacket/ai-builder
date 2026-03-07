# Lesson 021 — Specialist Agents vs Single Generalist

**Category:** ai-collaboration
**Source project:** Cornjacket Platform
**Date:** 2026-02-13

## Context

A single AI agent handling all roles — coding, committing, research, documentation, task tracking — creates the "distracted agent" anti-pattern. Attention dilution causes missed instructions and sloppy output. The alternative is a team of specialist agents with defined roles and document permissions.

## Lesson

A single monolithic agent works for small tasks but degrades on complex work where multiple concerns compete for attention. Specialist agents (implementer, reviewer, committer, architect, documenter) with explicit role boundaries and document permissions produce more focused output. However, spinning up a full team for every task is impractical — use specialists on the main branch where coordination matters, and a single capable agent per feature branch where speed matters.

## Decision Guidance

When a project grows beyond simple tasks, define specialist roles with:
- Clear boundaries (what each agent does and doesn't do)
- Document permissions (read/write/none per directory per agent)
- Communication patterns (outbox/inbox for async handoffs)
- Operating modes (specialist team vs jack-of-all-trades depending on context)

Start with the highest-value separation first: split the committer from the implementer to enforce diff review.

## Related Lessons

- [018](018-review-ai-diffs-before-committing.md) — first use case for agent separation
- [019](019-instruction-file-design.md) — per-agent instruction files replace monolithic CLAUDE.md
