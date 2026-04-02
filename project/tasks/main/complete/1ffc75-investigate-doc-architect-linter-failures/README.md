# Task: investigate-doc-architect-linter-failures

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Next-subtask-id | 0003 |

## Goal

Investigate why DOC_ARCHITECT fails the POST_DOC_HANDLER linter on almost every
first attempt, determine the root cause, and fix either the prompt or the linter
so that first-attempt pass rate is high.

## Context

Both doc regression execution logs show a systematic pattern: every atomic leaf
component fails `POST_DOC_HANDLER` on the first DOC_ARCHITECT attempt, then passes
on the retry. This means every leaf costs two AI invocations instead of one.

**doc-user-service:** `handlers` fails ATOMIC, retries, passes.

**doc-platform-monolith:** `platform`, `authz`, `store`, `handlers` all fail
ATOMIC on first attempt. One `integrate` node also fails INTEGRATE on first attempt.
That is 5 out of 6 leaves failing first-pass.

This is not flakiness — the failure rate is too consistent. Either:
- DOC_ARCHITECT's prompt does not fully specify what the linter requires, or
- The linter is checking for things the prompt does not tell DOC_ARCHITECT to produce

Each failed attempt wastes a full AI invocation. At ~1 minute and ~$0.01–0.05 per
call, this is a significant cost and time overhead across all doc pipeline runs.

Brainstorm: `sandbox/brainstorms/brainstorm-doc-architect-linter-failures.md`

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-1ffc75-0000-brainstorm](X-1ffc75-0000-brainstorm/)
- [x] [X-1ffc75-0001-surface-retry-warnings-in-summary](X-1ffc75-0001-surface-retry-warnings-in-summary/)
- [x] [X-1ffc75-0002-fix-linter-empty-section-regex](X-1ffc75-0002-fix-linter-empty-section-regex/)
<!-- subtask-list-end -->

## Notes

_None._
