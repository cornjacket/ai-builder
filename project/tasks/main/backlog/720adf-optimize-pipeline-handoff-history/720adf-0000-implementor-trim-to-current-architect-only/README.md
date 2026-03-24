# Task: implementor-trim-to-current-architect-only

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 720adf-optimize-pipeline-handoff-history             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Limit the handoff history passed to IMPLEMENTOR to only the immediately
preceding ARCHITECT entry (the design for the current component), rather
than the full ancestor lineage. Run a platform-monolith regression to
measure token savings and confirm that implementation quality is maintained.

## Context

In a 2-level decomposition, IMPLEMENTOR currently sees:
`ARCH/root → DECOMP/root → ARCH/parent → DECOMP/parent → ARCH/component`

The hypothesis is that IMPLEMENTOR only needs the current ARCHITECT design
(`ARCH/component`) to do its job — the parent decomposition rationale is
already embedded in the job doc it reads. Trimming to just
`handoff_history[-1]` would remove 2–4 entries per invocation.

**Risk:** Medium. Test carefully — IMPLEMENTOR on integration tasks may
genuinely need to know the parent's component boundary decisions. Compare
gold test results and generated code quality between trimmed and baseline
runs before declaring success.

**Implementation options:**
- A `handoff_depth: 1` field per role in the machine JSON (most flexible)
- A hardcoded IMPLEMENTOR filter in the orchestrator (simpler, less general)

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
