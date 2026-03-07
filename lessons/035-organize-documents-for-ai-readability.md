# Lesson 035 — Organize Documents for AI Readability

**Category:** architecture
**Source project:** Cornjacket Platform
**Date:** 2026-02-13

## Context

Large, monolithic documents are problematic for AI agents due to context window limitations and the "lost in the middle" phenomenon, where important details are overlooked within extensive text blocks.

## Lesson

Adopt a structured, hierarchical approach where large documents are refactored into index documents that point to smaller, focused child documents. The index contains brief summaries and links; child documents contain full details in subfolders.

When to refactor:
- **Document becomes too large** — turn it into an index, move content to child files
- **Section becomes too detailed** — extract to a child document, replace with summary and link

This lets AI agents read the index first, identify relevant sections, and load only what they need — avoiding wasted context tokens on irrelevant content.

## Decision Guidance

When a document covers multiple distinct topics or exceeds a manageable size, convert it to the index pattern. The design-spec split (one 955-line file → 15 focused files with a summary index) is the reference example. Prioritize this refactoring for documents that AI agents read frequently.

## Related Lessons

- [013](013-concise-output-reduces-token-waste.md) — conciseness complements structural organization
- [023](023-big-doc-threshold.md) — defines when to trigger the split
- [022](022-selective-reference-doc-loading.md) — organized docs enable selective loading
