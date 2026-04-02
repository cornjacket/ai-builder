# Task: doc-integrator-synthesis-rules

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Priority    | —           |
| Next-subtask-id | 0003 |

## Goal

Replace the vague "when applicable" guidance in `DOC_INTEGRATOR.md` with
deterministic rules for when `data-flow.md` and `api.md` must be produced.

## Context

Currently both synthesis docs are produced at the AI's discretion, making
pipeline output non-deterministic and gold tests unable to assert their
existence.

**New rules:**

- `data-flow.md` — **always produce** at every composite node. Components
  in the same composite directory always share a data path by definition;
  there is no meaningful case where the flow is absent.

- `api.md` — produce **if and only if** the composite exposes HTTP routes
  that are not fully documented within the sub-component docs. Fully
  documented means every route has a companion doc in the relevant
  sub-component. If the sub-components each document their own endpoints
  completely, a synthesis `api.md` is not needed here.

The implementation updates `DOC_INTEGRATOR.md` and the regression gold
tests for both `doc-user-service` and `doc-platform-monolith`.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-b4a146-0000-implement-synthesis-rules](X-b4a146-0000-implement-synthesis-rules/)
- [x] [X-b4a146-0001-update-doc-user-service-gold-test](X-b4a146-0001-update-doc-user-service-gold-test/)
- [x] [X-b4a146-0002-update-doc-platform-monolith-gold-test](X-b4a146-0002-update-doc-platform-monolith-gold-test/)
<!-- subtask-list-end -->

## Notes

_None._
