# Task: implement-decomposition-in-orchestrator

| Field    | Value                |
|----------|----------------------|
| Status | in-progress |
| Epic     | main             |
| Tags     | orchestrator, decomposition             |
| Parent   | —           |
| Priority | HIGH         |

## Description

Implement multi-level decomposition support in the orchestrator. The protocol
is designed and documented in `ai-builder/orchestrator/decomposition.md` —
this task makes it work in code.

**Gated by:**
- `7e7184-design-decomposition-protocol` — design must be complete first
- `d3616d-rename-pipeline-outcomes-for-clarity` — all outcome names must be
  finalised before decomposition routes are implemented; do not write code
  against old outcome strings

## Documentation

Update `ai-builder/orchestrator/routing.md` and `orchestrator.md` to reflect
any implementation decisions made during this work.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [f2e7aa-add-decomposition-routes-to-orchestrator](f2e7aa-add-decomposition-routes-to-orchestrator/)
- [x] [0583cf-expand-tm-prompt-for-decompose-mode](0583cf-expand-tm-prompt-for-decompose-mode/)
- [x] [7f8d69-expand-tm-prompt-for-stop-after](7f8d69-expand-tm-prompt-for-stop-after/)
- [x] [47412e-create-decomposition-job-templates](47412e-create-decomposition-job-templates/)
- [x] [0551e4-update-architect-prompt-for-decomposition](0551e4-update-architect-prompt-for-decomposition/)
- [ ] [d5dad2-add-decomposition-regression-test](d5dad2-add-decomposition-regression-test/)
- [ ] [3cbd2e-702059-add-start-role-flag-to-orchestrator](3cbd2e-702059-add-start-role-flag-to-orchestrator/)
<!-- subtask-list-end -->

## Notes

_None._
