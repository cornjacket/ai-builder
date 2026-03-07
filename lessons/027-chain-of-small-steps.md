# Lesson 027 — Chain of Small Verifiable Steps

**Category:** process
**Source project:** Cornjacket Platform
**Date:** 2026-02-13

## Context

Complex tasks succeed when broken into small increments with verification between each one. Without this discipline, AI agents may attempt large leaps that compound errors — each wrong assumption builds on the previous one, and by the time a test fails, the root cause is buried under multiple changes.

## Lesson

Break complex tasks into the smallest verifiable increments. After each step, verify correctness before proceeding to the next. If a step fails, fix it before moving on — do not accumulate errors. Each step should produce an observable, testable result.

## Decision Guidance

When a task involves more than 2-3 changes, decompose it into steps where each step can be independently verified. Prefer a sequence of small, correct changes over one large change that might be wrong. The overhead of verification at each step is far less than the cost of debugging a large broken change.

## Related Lessons

- [026](026-verify-assumptions-before-implementing.md) — verify before you start, then work in small steps
- [003](003-every-change-needs-a-task-document.md) — task docs naturally encourage decomposition
