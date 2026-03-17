# Task: resolve-pipeline-spec-adherence-failure

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | regression-test, roles  |
| Priority    | HIGH                    |

## Goal

Diagnose and fix why the pipeline does not faithfully implement the full API
spec given in a job document. Then re-run the platform-monolith regression
test to verify all gold tests pass.

## Context

First run of `tests/regression/platform-monolith/` (2026-03-16) resulted in
`TM_ALL_DONE` (pipeline completed) but the gold test failed. The IMPLEMENTOR
produced a partial, spec-deviant IAM service:

| Spec | Built | Failure |
|------|-------|---------|
| `POST /users` body: `{"username","password"}` | `{"name","email"}` | 400 on all user ops |
| `GET /roles` | POST-only on `/roles` | 404 |
| `GET /users/{id}/roles` | `/users/{id}/permissions` | wrong path |
| `/auth/login`, `/auth/logout` | not implemented | missing |
| `/authz/check` | not implemented | missing |

Metrics service (port 8081) passed all gold tests correctly.

Root cause hypothesis: the ARCHITECT simplified the IAM decomposition and the
IMPLEMENTOR stayed within that simplified scope rather than re-reading the
original spec. Possible fixes:
- Ensure ARCHITECT and IMPLEMENTOR are instructed to re-read the top-level
  job doc (the build-1 README) for the full API contract at every design step
- Add explicit acceptance criteria to the job doc that the TESTER must verify
  against the original spec endpoints
- Tighten ARCHITECT.md to require the full endpoint list be preserved in the
  component's Acceptance Criteria, not paraphrased or reduced

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [def6b9-fix-architect-decompose-contract-propagation](def6b9-fix-architect-decompose-contract-propagation/)
- [x] [e42376-rerun-platform-monolith-regression-test](e42376-rerun-platform-monolith-regression-test/)
- [x] [89e2cb-oracle-review-cc2203](89e2cb-oracle-review-cc2203/)
<!-- subtask-list-end -->

## Notes

_None._
