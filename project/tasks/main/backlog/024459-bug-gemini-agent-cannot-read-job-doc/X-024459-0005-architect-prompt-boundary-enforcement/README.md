# Task: architect-prompt-boundary-enforcement

| Field       | Value |
|-------------|-------|
| Task-type   | USER-SUBTASK |
| Status | complete |
| Parent      | 024459-bug-gemini-agent-cannot-read-job-doc |

## Goal

Strengthen ARCHITECT role prompt to prevent emitting implementation outcomes
and to use design language (not implementation language) for the integrate
component.

## Notes

Commit: `483743b`

Three changes to roles/ARCHITECT.md:
1. Added explicit rule at the top: "You do not write code. You do not run
   tests." and "Never emit an outcome that belongs to another role."
2. Changed integrate Level:TOP description from "produce a runnable entry
   point" (implementation language) to "design the entry point and component
   wiring" (design language).
3. Marked valid outcomes as "mode-specific — no other outcomes are permitted."

Root cause: Gemini's ARCHITECT on the integrate component interpreted the Goal
("produce a runnable entry point") as an implementation directive and emitted
IMPLEMENTOR_IMPLEMENTATION_DONE.
