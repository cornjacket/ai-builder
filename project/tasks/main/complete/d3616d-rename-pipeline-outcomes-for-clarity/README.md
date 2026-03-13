# Task: rename-pipeline-outcomes-for-clarity

| Field    | Value                |
|----------|----------------------|
| Status | complete |
| Epic     | main             |
| Tags     | orchestrator, routing             |
| Parent   | —           |
| Priority | HIGH         |

## Description

Rename all pipeline outcome values so every outcome is unambiguous about which
role produced it. Currently `DONE` and `FAILED` are used by multiple roles with
different meanings, which makes routing logic and logs harder to read.

**Renames:**

| Role | Old | New |
|------|-----|-----|
| IMPLEMENTOR | `DONE` | `IMPLEMENTATION_DONE` |
| TESTER | `DONE` | `TESTS_PASS` |
| TESTER | `FAILED` | `TESTS_FAIL` |

`NEED_HELP` and `NEEDS_ARCHITECT` are already role-scoped — no change needed.

**Touch points:**
- `ROUTES` table in `orchestrator.py`
- `build_prompt()` — valid outcomes listed in each role's prompt footer
- `roles/IMPLEMENTOR.md` and `roles/TESTER.md` — outcome instructions
- `ai-builder/orchestrator/routing.md` — routing reference doc
- Any regression test stubs or job fixtures that assert on outcome strings

**Gate:** `8eea17-implement-decomposition-in-orchestrator` depends on this task
being complete so decomposition is written against the final outcome names.

## Documentation

Update `ai-builder/orchestrator/routing.md` with the renamed outcomes.

## Subtasks

<!-- When a subtask is finished, run complete-subtask.sh to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
