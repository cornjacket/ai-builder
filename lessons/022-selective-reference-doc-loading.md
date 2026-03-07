# Lesson 022 — Selective Reference Doc Loading

**Category:** ai-collaboration
**Source project:** Cornjacket Platform
**Date:** 2026-02-13

## Context

AI agents in doc-heavy projects may over-read (loading every doc into context, wasting tokens) or under-read (missing critical information). Without a mapping of tasks to relevant docs, agents either guess which docs to read or load everything.

## Lesson

Create a discovery mechanism that maps task categories to relevant documents. This can be a manifest file with metadata, a librarian agent that consults an index, or a reference table in the instruction file. The goal is selective loading — agents read only what they need for the current task, not the entire doc tree.

## Decision Guidance

When your project has more than ~20 documentation files, well-named filenames alone are a brittle discovery mechanism. Add metadata (tags, categories, relevance hints) and an index that agents can consult. A dedicated librarian agent that resolves "what docs do I need for X?" keeps task-executing agents focused on their work.

## Related Lessons

- [035](035-organize-documents-for-ai-readability.md) — document organization enables selective loading
- [019](019-instruction-file-design.md) — instruction file points to discovery mechanism
