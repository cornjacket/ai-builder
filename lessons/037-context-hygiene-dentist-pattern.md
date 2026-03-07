# Lesson 037 — Context Hygiene: The Dentist Pattern

**Category:** ai-collaboration
**Source project:** Cornjacket Platform
**Date:** 2026-02-13

## Context

AI conversations degrade over time. As the context window fills, earlier instructions silently fade from attention — a phenomenon called "context rot." The problem is invisible: the AI doesn't announce that it has forgotten a rule. You only discover rot when something goes wrong (a missed task doc, a skipped review, a wrong assumption).

## Lesson

Schedule periodic "dentist check-ups" during long AI sessions. At regular intervals or after key triggers (context compression, task switches, suspected drift), have the AI recall the critical rules it is following, confirm its active role, and verify that expected context markers are still appearing. Missing markers or forgotten rules signal rot. The remedy is re-stating faded rules explicitly or starting a fresh conversation if rot is severe.

Key triggers for a check-up:
- Missing expected context markers in AI output
- AI makes an error consistent with a forgotten rule
- Conversation exceeds a length threshold
- After context window compression (summary)
- Switching between tasks or phases

## Decision Guidance

When setting up long-running AI workflows, build in context hygiene checkpoints. Don't wait for failures to detect rot — by then, damage is done. The cheapest intervention is asking "list the rules you're currently following" and comparing against the instruction file. Treat context rot the way you treat technical debt: catch it early, remediate immediately, and track patterns to improve your instruction design.

## Related Lessons

- [033](033-context-markers-for-rot-detection.md) — markers make rot visible; check-ups detect their absence
- [030](030-instruction-sandwich.md) — reinforcement is the remedy for detected rot
- [032](032-active-partner.md) — pushback is one of the first behaviors to fade
