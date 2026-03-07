# Lesson 023 — Define a Big Doc Threshold

**Category:** architecture
**Source project:** Cornjacket Platform
**Date:** 2026-02-13

## Context

Documentation files grow organically. Without a threshold, a single file can balloon to hundreds of lines, forcing agents to load irrelevant content to find what they need. Splitting large files into focused pieces with a summary index dramatically improves agent efficiency.

## Lesson

Define a "big doc" threshold (e.g., 200+ lines) and a process for splitting. After modifying a document, check its size. If exceeded, flag it for splitting. The split should be driven by the domain owner (who decides how to organize) and executed by the documenter (who does the restructuring). The summary-index-plus-detail-files pattern works well: the index gives a zoomed-out view, detail files provide depth.

## Decision Guidance

When a file exceeds your threshold, split it using the index pattern: rewrite the original as a summary with links to focused section files. Preserve all content — splitting is reorganization, not deletion. Apply the same threshold across all repos for consistency.

## Related Lessons

- [035](035-organize-documents-for-ai-readability.md) — organizing docs for AI readability
- [013](013-concise-output-reduces-token-waste.md) — large docs waste tokens
