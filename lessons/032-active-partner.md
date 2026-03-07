# Lesson 032 — Give AI Permission to Push Back

**Category:** ai-collaboration
**Source project:** Cornjacket Platform
**Date:** 2026-02-13

## Context

AI agents default to agreeableness — they follow instructions even when the instruction is flawed. Without explicit permission to disagree, the AI acts as an order taker rather than a collaborative partner, silently implementing suboptimal approaches.

## Lesson

Explicitly instruct the AI to push back when it identifies flawed logic, suboptimal approaches, or missing considerations. Include this in the instruction file as a standing order: "If my logic is flawed or my approach is suboptimal, say so directly." Then validate that this instruction actually works — AI agreeableness can override the instruction, especially in long conversations where it fades from attention.

## Decision Guidance

When setting up AI instructions, add a "push back" rule early and prominently. Periodically test it by presenting deliberately flawed approaches. If the AI stops pushing back, it's a signal of context rot — re-state the rule. The best AI collaborations happen when the AI treats the human as a peer, not a boss.

## Related Lessons

- [030](030-instruction-sandwich.md) — the pushback rule needs reinforcement as context grows
- [031](031-silent-misalignment.md) — pushback is one defense against silent misalignment
