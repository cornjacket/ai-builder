# Lesson 013: Concise Output Reduces Token Waste

## Context

AI agents tend toward verbose output — restating context, over-explaining decisions, padding documents with filler. Every token costs money, consumes context window, and buries signal in noise.

## Problem

Without explicit conciseness instructions, AI agents will:
- Restate what the user just said before answering
- Add unnecessary preamble and closing remarks
- Generate documents with redundant prose instead of tables/bullets
- Duplicate information that already exists elsewhere in the codebase

This wastes tokens on both input (bloated documents loaded as context) and output (verbose responses).

## Solution

Add an explicit conciseness rule to AI agent instructions (CLAUDE.md or equivalent). The rule should cover both conversational responses and generated artifacts (task docs, specs, commit messages, comments).

Key directives:
- Say what needs to be said, then stop
- Use tables and bullets over prose where possible
- Link to existing information instead of repeating it
- Omit context the user already knows

## Relationship to Other Lessons

- **Lesson 008** (Model Usage) — conciseness reduces cost regardless of which model is used
- **Lesson 012** (Chat vs Code) — even in the right interface, verbose output wastes tokens
