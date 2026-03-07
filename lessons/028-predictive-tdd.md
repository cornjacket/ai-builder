# Lesson 028 — Predictive TDD: Predict Before Running Tests

**Category:** process
**Source project:** Cornjacket Platform
**Date:** 2026-02-13

## Context

AI agents can write and run tests without understanding the code. When a test fails unexpectedly, the agent often brute-forces fixes (changing code until the test passes) instead of correcting its mental model. This produces fragile code that works by accident.

## Lesson

Before running any test, the AI must predict: which tests pass, which fail, and why. A wrong prediction means the AI's mental model is out of sync with the codebase — it must stop, re-read relevant code, explain the mismatch, and correct its understanding before continuing. Bad predictions get flagged prominently (🚨 **BAD PREDICTION** 🚨) as a forcing function to recalibrate. This applies to all executable operations where the outcome can be predicted, not just unit tests.

## Decision Guidance

When adding predictive TDD to your workflow, make it a hard requirement, not a suggestion. The prediction step costs seconds; brute-forcing a fix from a wrong mental model costs hours. Treat a bad prediction the same way you'd treat a failing test — it's a signal to stop and understand, not to try harder.

## Related Lessons

- [026](026-verify-assumptions-before-implementing.md) — predictive TDD is assumption verification applied to tests
- [027](027-chain-of-small-steps.md) — predict-run-verify is one small step in the chain
