# Task: strip-tester-handoff-history

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | b14e76-brainstorm-token-usage-and-caching-costs             |
| Priority    | —           |
| Next-subtask-id | 0001 |

## Goal

Add `TESTER` to `_HANDLER_ROLES` in `orchestrator.py` so TESTER receives no handoff history — only its role prompt and the job doc. Same pattern already applied to DECOMPOSE_HANDLER and LEAF_COMPLETE_HANDLER.

## Context

Run 8 data shows TESTER totalling 913,529 cached tokens across 5 invocations (~183K avg). TESTER doesn't use handoff history — it reads the job doc for acceptance criteria and runs `go test`. Stripping handoff should bring TESTER to the ~30K Claude Code floor, saving ~763K cached tokens per run (~13% of total).

One-line change: add `"TESTER"` to the `_HANDLER_ROLES` set in `orchestrator.py`. Apply the same change to `target/` copy if applicable. Run the platform-monolith regression test to verify token reduction and confirm pipeline still passes.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-b14e76-0000-no-history-flag-in-state-machine](X-b14e76-0000-no-history-flag-in-state-machine/)
<!-- subtask-list-end -->

## Notes

_None._
