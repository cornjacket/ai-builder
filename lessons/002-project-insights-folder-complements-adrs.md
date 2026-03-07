# Lesson 002 — Project Insights Folder Complements ADRs

**Category:** repo-structure
**Source project:** cornjacket-platform
**Date:** 2026-02-09

## Context

While building the platform, two distinct types of knowledge emerged during development:

1. **Architectural decisions** — "We chose Redpanda over Kafka because..." These are well-served by ADRs (Architectural Decision Records) with their formal status lifecycle (Proposed → Accepted → Superseded).
2. **Implementation insights** — "When wiring Go services to Redpanda, we discovered that consumer group rebalancing behaves differently under ECS task scaling." These are practical, hard-won lessons that don't fit the ADR format because they aren't *decisions* — they're *discoveries*.

ADR folders captured the "what and why" of architectural choices, but there was no home for the practical knowledge gained *during implementation* — the gotchas, patterns, and tips that would save time if the same situation arose again.

## Lesson

Create an `insights/` directory to capture implementation-level lessons learned. These are distinct from ADRs:

| | ADRs | Insights |
|---|---|---|
| **Content** | Architectural decisions with rationale | Practical discoveries and implementation knowledge |
| **Format** | Formal (status, context, decision, consequences) | Lightweight (context, insight, applicability) |
| **Lifecycle** | Proposed → Accepted → Deprecated → Superseded | Written once, updated if understanding deepens |
| **Scope** | System-wide design choices | Can be narrow (a single integration, library quirk, or deployment pattern) |

This gives developers a place to record "things I wish I knew when I started this" without stretching the ADR format beyond its purpose.

## Decision Guidance

When setting up a new project, create an `insights/` directory alongside any `decisions/` (ADR) directory. Use ADRs for choices that shape the system architecture. Use insights for practical implementation knowledge — integration gotchas, performance discoveries, tooling tips, and patterns that emerged during development. If you find yourself writing an ADR that has no real "decision" in it, it's probably an insight.

**Centralized vs. per-repo:** If the project has a shared documentation repo (like a `platform-docs/`), centralize all insights there rather than creating `insights/` folders in every repo. Use category subdirectories (e.g., `architecture/`, `development/`, `infrastructure/`) to organize by topic. This avoids fragmenting the collection across repos and keeps a single searchable source of truth. Only create per-repo insights folders when repos are owned by separate teams without a shared docs repo.

## Related Lessons

- [001 — Separate Meta-Learning from Project Repos](001-separate-meta-learning-from-project-repos.md): Lesson 001 covers the *project-agnostic* meta-learning repo. This lesson covers *project-specific* insights folders within each repo. Together they form two tiers: repo-level insights (specific to that codebase) and cross-project lessons (reusable everywhere).
