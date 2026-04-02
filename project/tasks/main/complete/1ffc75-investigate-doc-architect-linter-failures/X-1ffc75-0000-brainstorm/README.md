# Task: brainstorm

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 1ffc75-investigate-doc-architect-linter-failures             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Investigate the root cause of systematic first-attempt linter failures and document
findings and proposed fix in the brainstorm file.

## Context

Brainstorm file: `sandbox/brainstorms/brainstorm-doc-architect-linter-failures.md`

Steps:
1. Inspect the linter code (`agents/doc/linter.py`) — what exactly does it check?
2. Inspect DOC_ARCHITECT prompt (`machines/doc/roles/DOC_ARCHITECT.md`) — does it
   specify the output format the linter requires?
3. Find a failing doc from the regression (before retry) and compare against the
   linter rules to identify the specific check that fires
4. Determine whether the fix is in the prompt (add linter requirements to
   DOC_ARCHITECT instructions) or the linter (loosen a rule that is too strict)
5. Write findings and recommendation to the brainstorm file

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
