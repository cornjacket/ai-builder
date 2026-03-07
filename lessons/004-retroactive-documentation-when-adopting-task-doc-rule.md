# Lesson 004 — Retroactive Documentation: When Adopting a Task-Doc Rule Mid-Project

**Category:** process
**Source project:** cornjacket-platform
**Date:** 2026-02-09

## Context

After adopting the "every change needs a task document" rule (Lesson 003) mid-project, a gap existed: earlier work had been done without task documents. The temptation was to create retroactive task docs for those changes — but that would produce historical fiction (documents with fabricated timestamps describing decisions that were actually made differently).

The specific case: 12 test functions existed across 5 files, created as byproducts of Specs 007 and 008, plus one chat-initiated test with no task doc at all. Writing a retroactive "Spec 009: Add tests for clock and envelope" would misrepresent the actual development sequence — those tests were written *alongside* other features, not as a deliberate testing initiative.

## Lesson

When adopting a task-doc-first rule mid-project, **don't create retroactive documents for prior work.** Instead, use the next relevant spec as a **reconciliation point**:

1. Include a **Current State** section that inventories existing work and attributes its origins (which spec, which chat session, or "pre-rule")
2. Define the **baseline** going forward — what exists, what's missing, what's in scope
3. The reconciliation point becomes the "as of this document, here's where we are" marker

This preserves the key property of the task-doc system — **honesty about the development timeline** — while still closing the documentation gap. The reconciliation spec is genuinely a new piece of work (defining strategy, identifying gaps, planning next steps); the existing code it references is acknowledged as prior art, not claimed as its deliverable.

### When to use reconciliation points

- Adopting task-doc rules on an existing codebase (not just mid-project — also when onboarding a new team/process to an existing repo)
- After a burst of exploratory/prototyping work that preceded formal process
- When consolidating scattered changes that were individually too small for specs but collectively represent a coherent area

### When NOT to use them

- For a single missed task doc — just create the task doc normally and note it was written after the fact
- When the prior work is so small it doesn't need acknowledgment — a reconciliation point for one config tweak is overhead

## Decision Guidance

When adopting documentation-first rules on existing work, resist the urge to backfill. Backfilled documents look legitimate but poison the timeline — future readers (human or AI) can't distinguish real-time decisions from post-hoc rationalization. Instead, draw a line: acknowledge what exists, define what's next, and move forward with the rule applied consistently.

The reconciliation pattern scales: it works for a dozen tests, and it would work for an entire undocumented codebase being brought under a task-doc regime. The key is that the reconciliation document is itself honest — it says "here's what we found" rather than "here's what we decided."

## Related Lessons

- [003 — Every Change Needs a Task Document](003-every-change-needs-a-task-document.md): The rule that creates the need for reconciliation when adopted mid-project.
- [001 — Separate Meta-Learning from Project Repos](001-separate-meta-learning-from-project-repos.md): This lesson is a meta-process insight (how to handle documentation gaps), not a project-specific decision — it belongs here, not in an ADR.
