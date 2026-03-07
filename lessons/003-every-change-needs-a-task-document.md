# Lesson 003 — Every Change Needs a Task Document

**Category:** process
**Source project:** cornjacket-platform
**Date:** 2026-02-09

## Context

During AI-assisted development, changes to the codebase originate from two sources: formal planned features and ad-hoc instructions given in chat. The formal features had task documents, but chat-initiated changes (bug fixes, minor tweaks, config adjustments) often went straight to code with only a commit message as the record. This created gaps in the project's history — some changes had clear "why" documentation, others didn't.

The problem compounds over time: a commit history full of small undocumented changes makes it impossible to understand the full reasoning chain behind the current state of the codebase.

## Lesson

Enforce a universal rule: **every change to the codebase must have an accompanying task document, created before the code is modified.** No exceptions, regardless of how small the change is.

To make this practical, use two tiers of documentation sharing a single numbering sequence:

- **Specs** (heavyweight) — for features and significant changes that need design review. Include context, design, acceptance criteria.
- **Tasks** (lightweight) — for bug fixes, tweaks, and small changes. Include context, what changed, and how to verify.

The shared numbering preserves chronological ordering, so the task index reads as a complete narrative of how the codebase evolved.

For AI agents specifically: when a user gives an instruction in chat to modify code, the agent must create the task document *first*, then implement the change, then commit both together.

### Grouping to prevent proliferation

A strict "one doc per change" rule risks creating noise — three related logging fixes don't need three separate task documents. To balance traceability with readability:

- **Closely related tasks in the same session** can share a single task document. Each individual change is listed as a numbered item within the doc.
- The grouping criteria is **coherence**, not just timing. Changes must address the same area of concern (e.g., all logging fixes, all config tweaks). Unrelated changes in the same session still get separate task docs.
- Specs are never grouped — each spec is a distinct design unit.

This keeps the task index meaningful. A grouped task like `009-logging-cleanup.md` with 3 changes inside it is more informative than 3 separate single-line task docs.

## Decision Guidance

When setting up an AI-assisted project, establish the "every change needs a task doc" rule from day one. Use a lightweight template (3 fields: context, change, verification) so the overhead for small changes is minimal — just enough to capture intent. Allow related lightweight tasks to be grouped in a single document when they share the same area of concern and are done in the same session.

The key benefit is **replay capability**: from any tagged commit, you can read the subsequent task documents in sequence and reimplement the entire codebase. The task record becomes a specification log, not just a history — a future AI agent could replay the same tasks against a different tech stack entirely.

When choosing between spec and task: if the change requires a design decision or affects multiple components, it's a spec. If you can describe the change in a sentence or two and implement it immediately, it's a task. When choosing whether to group tasks: if the changes are closely related and done in the same session, group them; if they're unrelated, don't.

## Related Lessons

- [001 — Separate Meta-Learning from Project Repos](001-separate-meta-learning-from-project-repos.md): The task document rule generates project-specific knowledge, while lesson 001's meta-repo captures the process pattern itself.
- [002 — Project Insights Folder Complements ADRs](002-project-insights-folder-complements-adrs.md): ADRs capture architectural decisions, task docs capture implementation intent. Together with insights, they form three layers of project knowledge.
- [004 — Retroactive Documentation: When Adopting a Task-Doc Rule Mid-Project](004-retroactive-documentation-when-adopting-task-doc-rule.md): What to do when this rule is adopted mid-project and prior work has no task docs — use reconciliation points instead of backfilling.
