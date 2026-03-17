# Task: fix-architect-decompose-contract-propagation

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | roles, architect        |
| Parent      | cc2203-resolve-pipeline-spec-adherence-failure |
| Priority    | HIGH                    |

## Goal

Update `roles/ARCHITECT.md` decompose mode instructions so that each component
row carries the full API contract — both the complete endpoint signatures (path,
method, status codes) AND the full parameter models (request body field names
and types, response field names and types) for every endpoint assigned to that
component. This information must be propagated verbatim, not summarised.

## Context

In the platform-monolith regression run the ARCHITECT decomposed correctly at
the structural level but wrote one-line descriptions in the Components table
(e.g. "Metrics ingestion, port 8081"). TM copied those into component Goals.
By the time ARCHITECT ran in design mode, the full spec was gone — it invented
plausible-sounding but spec-deviant schemas (`{"name","email"}` instead of
`{"username","password"}`), missing endpoints (`/auth/login`, `/auth/logout`,
`/authz/check`), and renamed routes (`/users/{id}/permissions` instead of
`/users/{id}/roles`).

There are two distinct things that must be propagated — both are required:

1. **Full API routes** — every endpoint assigned to this component: path,
   method, success status code, error status codes. A design-mode ARCHITECT
   must not have to guess which routes belong to a component.

2. **Full parameter models** — for every endpoint: the complete request body
   field names and types, and the complete response field names and types.
   Without this, the ARCHITECT invents field names that diverge from the spec.

The fix location is `roles/ARCHITECT.md` decompose mode, step 4: replace the
`<one-line responsibility>` description instruction with a requirement to write
the full API contract (routes + parameter models) for each component.

After fixing, re-run the platform-monolith regression test to verify all gold
tests pass.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
