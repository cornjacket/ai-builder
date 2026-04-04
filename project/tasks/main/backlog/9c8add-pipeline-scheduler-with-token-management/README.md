# Task: pipeline-scheduler-with-token-management

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Category    | orchestrator-core      |
| Next-subtask-id | 0000               |

## Goal

Build a scheduler that accepts pipeline job definitions, checks token
availability before launching, postpones jobs when quota is insufficient,
and automatically reschedules when tokens are available again.

## Context

Pipeline runs currently fail mid-run when rate limits are hit, requiring
manual detection and resume. The scheduler eliminates this by checking
quota before launch.

**Proposed workflow:**
1. Oracle (or CI) submits a job to the scheduler: `schedule-job.sh --job
   <README> --target-repo <dir> --output-dir <dir> --state-machine <json>`
2. Scheduler checks current token availability (from `74d718`).
3. Scheduler projects token cost for this job (from `68887a`).
4. If projected cost ≤ available quota: launch immediately via orchestrator.
5. If projected cost > available quota: record the job in a queue file
   (`scheduler/queue.json`); poll for availability at the reset interval;
   launch when quota is sufficient.
6. After each run: log actual vs projected tokens to improve future estimates.

**Key design questions:**
- Queue persistence: file-based (`scheduler/queue.json`) or in-memory?
- Polling mechanism: cron, sleep loop, or OS scheduler?
- Concurrency: one job at a time (simplest) or parallel with per-job quotas?
- Failure handling: if a job fails mid-run (non-quota error), does the
  scheduler retry or surface for manual intervention?

**Depends on:**
- `74d718-research-claude-token-availability` — quota check mechanism
- `68887a-project-pipeline-token-and-time-cost` — projection model

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
