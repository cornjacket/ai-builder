# Lesson 024 — The Perfect Recall Fallacy

**Category:** ai-collaboration
**Source project:** Cornjacket Platform
**Date:** 2026-02-13

## Context

AI agents are often treated as if they perfectly remember all library APIs, framework details, and version-specific behavior. In reality, their training data has a cutoff date, may contain errors, and lacks details about recent releases or niche libraries.

## Lesson

Never assume the AI perfectly recalls library APIs. Before using a library extensively, ground the AI in current documentation: run `go doc`, fetch official docs, check project-specific notes, or create sandbox experiments to verify API behavior. For frequently-used libraries, maintain a reference doc summarizing key APIs and gotchas. Use research expert tools (e.g., NotebookLM) to digest and summarize library documentation when needed.

## Decision Guidance

When starting work with a library the AI hasn't used in the current session, verify key APIs against current docs before writing production code. The cost of a quick `go doc` check is seconds; the cost of debugging an incorrect API assumption is hours. For critical or unfamiliar libraries, write a small sandbox experiment first.

## Related Lessons

- [005](005-abstract-test-infrastructure-for-local-vs-ci.md) — test infrastructure relies on library APIs
