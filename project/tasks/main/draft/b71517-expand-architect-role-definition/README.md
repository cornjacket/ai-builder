# Task: expand-architect-role-definition

| Field    | Value                |
|----------|----------------------|
| Status   | draft           |
| Epic     | main             |
| Tags     | orchestrator, roles, architect             |
| Parent   | —           |
| Priority | MED         |

## Description

The current ARCHITECT prompt is a minimal stub (4 lines). Once role
definitions are extracted to `roles/ARCHITECT.md`, expand it to cover the
rules and responsibilities that regression testing reveals are missing.

**Do not expand speculatively.** Rules should be added in response to
observed failures in regression tests — not anticipated failures. The
current stub may be sufficient for simple jobs; gaps will surface through
testing.

**Known areas likely to need coverage (to validate through testing):**
- Directory structure decisions and when a new directory warrants a CLAUDE.md
- How to scope subtasks so IMPLEMENTOR sessions don't hit context rot
- When to set `Stop-after` on a subtask (exceptional cases only)
- How to write Acceptance Criteria that are machine-checkable by the TESTER

## Documentation

Update `roles/ARCHITECT.md` with expanded rules as they are identified.
No changes to `CLAUDE.md` needed — role definitions are not agent instructions
for this repo.

## Notes

Depends on `6fdb3a-consolidate-role-definitions` completing first — the role
file needs to exist before it can be expanded.

Evolution path: extract stub → run regression tests → add rules where tests
reveal gaps → repeat. Avoid front-loading rules that may never be needed.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
