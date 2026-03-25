# Task: orchestrator-role-specific-outcome-validation

| Field       | Value |
|-------------|-------|
| Task-type   | USER-SUBTASK |
| Status | complete |
| Parent      | 024459-bug-gemini-agent-cannot-read-job-doc |

## Goal

Replace the orchestrator's loose outcome validation with a role-specific check
that halts with a clear error when an agent emits another role's outcome.

## Notes

Commit: `e5f53c0`

The previous check (outcome not in [o for (_, o) in ROUTES]) tested whether
the outcome existed anywhere in the state machine — not whether it was valid
for the current role. ARCHITECT emitting IMPLEMENTOR_IMPLEMENTATION_DONE passed
this check, then ROUTES.get(("ARCHITECT", "IMPLEMENTOR_IMPLEMENTATION_DONE"))
returned None, silently exiting the loop as "pipeline complete."

Fix: collect valid_for_role = [o for (r, o) in ROUTES if r == current_role]
and check against that. Distinguishes "wrong role's outcome" from "unrecognised
outcome" in the error message.
