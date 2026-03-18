# Task: add-token-usage-regression-baseline

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

Add token usage assertions to the regression tests so that a code change causing a
significant increase in token consumption is caught before it reaches production.

## Context

The platform-monolith run (2026-03-17) established a baseline:
- 24 invocations, 4,794,984 cached tokens, 100,470 output tokens
- LEAF_COMPLETE_HANDLER: avg 1m 03s, 1,163,148 total tokens across 5 invocations

After the handoff-scoping fix (parent task + subtask 0000), these numbers should drop
significantly. We need a way to detect if a future change reverses that improvement or
introduces a new form of token bloat.

Design options to evaluate:
1. **run-metrics.json assertions**: after a pipeline run, the gold test reads the
   `run-metrics.json` output artifact and asserts per-role token totals are within
   a tolerance band of the baseline (e.g. ±20%)
2. **Per-invocation cap**: fail if any single invocation exceeds a token threshold
   (e.g. a handler invocation over 50k cached tokens is a red flag)
3. **Relative comparison**: store the baseline in the gold test and flag if any role's
   avg tokens-per-invocation increases more than N% from baseline

The simplest starting point is option 1: read `run-metrics.json` and assert total
cached tokens stay under a ceiling. The ceiling should be set after the fix is in place,
not using the current inflated baseline.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
