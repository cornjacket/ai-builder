# Lesson 033 — Context Markers for Rot Detection

**Category:** ai-collaboration
**Source project:** Cornjacket Platform
**Date:** 2026-02-13

## Context

As AI conversations grow, earlier instructions silently fade from attention. There is no observable signal that a rule has stopped being followed — the human only discovers it when something goes wrong.

## Lesson

Assign visual markers (emojis, bracket prefixes) to specific rules and agent roles. When a rule is applied, its marker appears in the output. When a marker stops appearing during operations where it should be present, that's an observable signal of context rot — the rule has faded from the AI's attention. This turns an invisible problem (context rot) into a visible one (missing markers).

Two levels: (1) agent role markers like `[IMPL]`, `[ARCH]` that show which agent is active, and (2) rule compliance markers like 🎯 (prediction made), 📋 (task doc created), 🔍 (assumptions verified) that confirm specific rules are being followed.

## Decision Guidance

When defining AI workflow rules, assign each critical rule a distinct emoji marker. Instruct the agent to display the marker when the rule is applied. If you stop seeing expected markers during specific operations, re-state the rule explicitly. This is cheap insurance against context rot — the marker system costs nothing to implement and makes rule compliance visible.

## Related Lessons

- [030](030-instruction-sandwich.md) — missing markers trigger instruction reinforcement
- [021](021-specialist-agents-vs-single-generalist.md) — role markers confirm which agent is active
