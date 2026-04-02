# Task: research-claude-token-availability

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Determine whether the Claude CLI or API exposes the current token quota and
remaining availability so the orchestrator can check before starting a run.

## Context

Pipeline runs hit rate limits mid-run (as seen in the doc-pipeline regressions),
wasting partial work and requiring manual resume. Before building a scheduler
(see `9c8add-pipeline-scheduler-with-token-management`), we need to know:

1. Does `claude` CLI expose remaining tokens / rate-limit reset time?
   - Check `claude --help`, `claude /status`, any `--output-format json` flags.
2. Does the Anthropic API expose quota or rate-limit headers?
   - Check `x-ratelimit-*` response headers on the Messages API.
3. Is there a polling endpoint or webhook that signals when limits reset?
4. What granularity is available — per-minute, per-hour, per-day, per-billing-
   period?

Output: a short findings doc (`sandbox/research-token-availability.md`)
summarising what is and isn't available, with enough detail to inform the
scheduler design.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
