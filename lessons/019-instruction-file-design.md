# Lesson 019 — Instruction File Design (Ground Rules)

**Category:** ai-collaboration
**Source project:** Cornjacket Platform
**Date:** 2026-02-13

## Context

AI coding tools load permanent instruction files (CLAUDE.md, .cursorrules, GEMINI.md) at the start of every session. These "ground rules" files define how the AI behaves. As projects grow, these files tend to bloat with role-specific details, architecture notes, and process descriptions — diluting the critical rules.

## Lesson

Keep instruction files focused on common guidelines that apply to ALL agents in ALL contexts. Move detailed content to separate files (per-agent instructions, process docs, reference docs) and use the instruction file as an index with pointers. The instruction file should be small enough that every rule gets attention, not so large that important rules get lost in noise.

## Decision Guidance

When your instruction file exceeds ~100-150 lines, audit it. Ask: does every rule here apply to every task? If not, extract role-specific content into separate files. Use a discovery mechanism (manifest, librarian agent, or reference index) so agents find detailed docs when needed rather than loading everything upfront.

## Related Lessons

- [013](013-concise-output-reduces-token-waste.md) — conciseness applies to instruction files too
- [035](035-organize-documents-for-ai-readability.md) — document organization for AI consumption
