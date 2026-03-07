# Lesson 031 — Silent Misalignment: When the AI Agrees But Is Wrong

**Category:** ai-collaboration
**Source project:** Cornjacket Platform
**Date:** 2026-02-13

## Context

AI agents rarely say "I don't understand" or "I'm not sure." Instead, they agree and proceed with a wrong internal model. The mismatch between what the human expects and what the AI believes only surfaces at runtime — when the implementation breaks.

## Lesson

Require the AI to show its plan before executing non-trivial changes. The plan should include: what will be changed, in what order, and what assumptions are being made. This makes the AI's mental model visible and gives the human a chance to catch misalignment before work is wasted. For trivial changes (typos, single-line fixes), skip the plan step.

## Decision Guidance

When an AI confidently agrees and immediately starts implementing, that's the highest-risk moment for silent misalignment. The more confident and fast the AI seems, the more important it is to pause and ask "show me what you're about to do." Combine with predictive TDD — wrong predictions are the strongest signal of misalignment.

## Related Lessons

- [026](026-verify-assumptions-before-implementing.md) — showing the plan surfaces assumptions
- [028](028-predictive-tdd.md) — wrong predictions expose misalignment
