# Lesson 034 — Human Prompting Best Practices

**Category:** ai-collaboration
**Source project:** Cornjacket Platform
**Date:** 2026-02-13

## Context

Most AI workflow guidance focuses on how to instruct the agent. But the human side of the collaboration matters just as much. Poor prompting habits — leading questions, order-taking framing, verbose descriptions of things that could be drawn — limit the AI's effectiveness.

## Lesson

Three key human-side disciplines for effective AI collaboration:

1. **Avoid answer injection** — Don't frame questions that limit the AI's options. Bad: "Should we use Redis for caching?" Good: "What caching approach fits our constraints?" Open-ended questions produce better solutions.

2. **Reverse direction** — Ask the AI for multiple suggestions rather than treating it as an order taker. "Give me 3 approaches for X with trade-offs." Then consider mixing and matching the best features from each approach into a superior combined implementation.

3. **Text native** — Use ASCII diagrams, markdown tables, and directory trees when communicating with AI. If something can be drawn, draw it instead of describing it. Visual formats are more precise and consume fewer tokens than prose.

## Decision Guidance

When collaborating with AI, default to open-ended questions and request multiple options. Resist the urge to prescribe a solution — let the AI explore the solution space first, then narrow down. Use visual text formats (tables, diagrams, trees) as the default communication medium. These habits produce better results regardless of which AI tool you use.

## Related Lessons

- [032](032-active-partner.md) — open-ended questions complement pushback permission
- [013](013-concise-output-reduces-token-waste.md) — text-native communication reduces tokens
