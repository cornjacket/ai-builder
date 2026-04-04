# Worktree Class Definitions

Each task has a `Category:` field that assigns it to one of the classes below.
Tasks in the same class touch the same files and should be worked in the same
worktree. Tasks in different classes can run in parallel with minimal merge
conflicts.

Full analysis: [`4a8789-investigate-task-partitioning-for-parallel-worktrees`](main/in-progress/4a8789-investigate-task-partitioning-for-parallel-worktrees/README.md)

---

## Class 1 — Gemini Compatibility

**Worktree branch:** `gemini-compat`
**Core files:** `ai-builder/orchestrator/orchestrator.py`, `agent_wrapper.py`, `gemini_compat.py`, `machines/builder/*.json`

Fixes and features for Gemini CLI as a pipeline agent: token/stream parsing,
sandboxed file tool workarounds, per-role model selection, agent-specific
prompt addenda in machine JSON.

**Tasks:** e62647, ec6a38, 024459, 66251c, 4f9fba, d99044

---

## Class 2 — Orchestrator Core

**Worktree branch:** `orchestrator-core`
**Core files:** `ai-builder/orchestrator/orchestrator.py`, `agents/builder/lch.py`, `agents/builder/decompose.py`, `render_readme.py`, `metrics.py`, `machines/builder/default.json`

Structural refactors and performance work inside the orchestrator: parallel
component execution, LCH cold-start reduction, shared agent relocation,
unit-testable decomposition, handoff history trimming, always-on recording,
pipeline scheduler.

**Must start after Class 1 is merged** — both classes touch `orchestrator.py` heavily.

**Tasks:** 720adf, ba683a, aa0f2f, eb5761, 154422, b48722, 9c8add, afed3c, 3d9f24

---

## Class 3 — Acceptance Spec & Prompt Quality

**Worktree branch:** `acceptance-spec` _(earmarked, new worktree required)_
**Core files:** `machines/builder/roles/ARCHITECT.md`, `machines/builder/roles/IMPLEMENTOR.md`, `machines/builder/default.json` (new state), `orchestrator.py` (new state dispatch)

Adds ACCEPTANCE_SPEC_WRITER stage to anchor the API contract before decomposition.
Also includes role prompt trimming and ARCHITECT expansion.

**Tasks:** f5f7b8, b71517, 403a88

---

## Class 4 — New Pipeline Modes

**Worktree branch:** `new-pipelines`
**Core files:** `ai-builder/orchestrator/machines/review/` (new), `machines/update/` (new), new role prompt files

Adds review and update pipeline modes as new machine configs and role prompts.
Minimal overlap with existing files.

**Tasks:** fe6b43, b7249c

---

## Class 5 — Regression Infrastructure

**Worktree branch:** `regression-infra`
**Core files:** `tests/regression/*/`, `tests/regression/goldutil/`, `tests/stage/` (new)

Test infrastructure: stale README updates, reorganising component tests into
stage tests, run-history tracking, gold test budget checks, execution log
validation, Docker container isolation.

**Tasks:** b13566, 705550, ba2238, 9df5ca, 818b46, 26d8ee, 5aea78

---

## Class 6 — Task Management & Dev Tooling

**Worktree branch:** `task-tooling`
**Core files:** `project/tasks/scripts/*.sh`, `CLAUDE.md`, `project/status/`

New and improved task management scripts, session context document, regression
permission enforcement in CLAUDE.md.

**Tasks:** 697e5a, 23450c, 1aba9b, ef40e2, f48538, 99c172

---

## Class 7 — Documentation

**Worktree branch:** `docs`
**Core files:** `ai-builder/docs/`, `learning/`, companion `.md` files

Documentation reorganisation, Claude vs Gemini behavioural difference docs,
task system usage guides.

**Tasks:** 88ba5d, 99ed0c, f1b888, 2da360, 16e107

---

## Class 8 — Workspace & Infrastructure

**Worktree branch:** `workspace-mgmt`
**Core files:** `bootstrap/new-worktree.sh`, `bootstrap/remove-worktree.sh`, workspace-level `CLAUDE.md`, GitHub settings

Cross-worktree memory sync, regression manager session design, workspace
CLAUDE.md boundary, GitHub branch protection.

**Tasks:** b4d83d, 15bff5, 3230ef, 69f69b

---

## Conflict Hotspots & Merge Order

`orchestrator.py` is touched by Classes 1, 2, and 3. Recommended merge order:

```
1 → 3 → 5/6/7 (parallel) → 4 → 2 → 8
```

Classes 3, 5, 6, 7 are safe to run in parallel with each other at any time.
Start Class 2 only after Classes 1 and 3 are merged.
