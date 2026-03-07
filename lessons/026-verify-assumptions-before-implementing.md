# Lesson 026 — Verify Assumptions Before Implementing

**Category:** process
**Source project:** Cornjacket Platform
**Date:** 2026-02-13

## Context

AI agents make assumptions and implement based on them without verifying. When assumptions are wrong, work must be redone. Observed: assuming `../` resolved to the workspace root from a bare repo (it didn't — needed `../../`), assuming `git clone --bare` configured fetch refspecs (it doesn't).

## Lesson

Before implementing, state critical assumptions explicitly and verify each one with evidence: run a command, read a file, check a path, test a small example. Do not assume something works without evidence. If verification is not possible, flag the assumption as unverified and proceed with extra caution.

## Decision Guidance

When an AI agent is about to implement something that depends on system behavior (file paths, tool defaults, library APIs), require verification before proceeding. The cheaper the verification (a quick `ls`, `go doc`, or test command), the less excuse for skipping it. Treat unverified assumptions as technical debt.

## Related Lessons

- [016](016-commit-task-doc-before-implementation.md) — task doc is a checkpoint before implementation
- [024](024-perfect-recall-fallacy.md) — library API assumptions are a specific category
