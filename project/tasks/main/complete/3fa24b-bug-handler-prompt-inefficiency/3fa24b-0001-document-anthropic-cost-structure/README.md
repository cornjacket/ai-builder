# Task: document-anthropic-cost-structure

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 3fa24b-bug-handler-prompt-inefficiency             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Create a reference document covering Anthropic's token pricing tiers so we can reason
accurately about what pipeline runs actually cost and where the money goes.

## Context

The platform-monolith run produced 4,795,236 total tokens: 252 new input, 100,470 output,
4,694,514 cached. Without understanding the pricing tiers these numbers are hard to
interpret for cost or optimization purposes.

Anthropic charges differently for each category:
- **Input tokens** (new, uncached): highest rate
- **Cache write tokens**: charged when content is first stored in the prompt cache
- **Cache read tokens** (cached): lowest rate — roughly 10x cheaper than new input
- **Output tokens**: separate rate, typically higher than input

The document should cover:
- Current rates for each token type (Sonnet 4.x, Opus 4.x, Haiku 4.x)
- How prompt caching works: what gets cached, TTL, when cache writes are charged
- A worked example using the platform-monolith run data
- Implications for pipeline design: output tokens and new input are the expensive dials;
  cached reads are cheap but still affect latency
- Where to find up-to-date pricing (Anthropic pricing page)

Output: a document at `docs/anthropic-cost-structure.md`.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
