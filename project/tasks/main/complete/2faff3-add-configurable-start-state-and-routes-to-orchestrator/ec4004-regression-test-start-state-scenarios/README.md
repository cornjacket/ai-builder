# Task: regression-test-start-state-scenarios

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 2faff3-add-configurable-start-state-and-routes-to-orchestrator             |
| Priority    | —           |

## Goal

Update all regression test `reset.sh` files to explicitly pass
`--state-machine`, then run each test end-to-end and verify the gold test
passes.

## Context

The orchestrator now loads a JSON machine file (`--state-machine`) instead of
using hardcoded `AGENTS` and `ROUTES`. The flag is optional — the orchestrator
defaults to `machines/default.json` (TM mode) or `machines/simple.json`
(non-TM mode) — but the reset.sh hint text should be explicit so it documents
exactly which machine each test uses.

Three regression tests to update and run:
1. `fibonacci` — flat mode, uses `machines/simple.json`
2. `user-service` — TM mode (single-level decomposition), uses `machines/default.json`
3. `platform-monolith` — TM mode (multi-level decomposition), uses `machines/default.json`

Each test: update reset.sh hint → reset → run pipeline → run gold test.
Results recorded in Notes below.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

### 2026-03-16 — Results

All three regression tests updated and green.

**fibonacci** (flat mode, `machines/simple.json`):
- reset.sh updated with explicit `--state-machine` hint
- Gold test: `ok` (1.18s)

**user-service** (TM mode, `machines/default.json`):
- reset.sh updated with explicit `--state-machine` hint
- Gold test: 8/8 pass (4.14s)

**platform-monolith** (TM mode multi-level, `machines/default.json`):
- reset.sh updated with explicit `--state-machine` hint
- Fixed stale `targetDir` reference in gold_test.go (leftover variable name from prior refactor)
- Gold test: 17/17 pass (4.42s)

Backward compatibility confirmed: no `--state-machine` flag changes required in
existing invocations — defaults select the correct machine file automatically.
