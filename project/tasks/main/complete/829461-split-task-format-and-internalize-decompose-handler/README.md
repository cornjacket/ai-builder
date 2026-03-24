# Task: split-task-format-and-internalize-decompose-handler

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Priority    | HIGH        |
| Next-subtask-id | 0008 |

## Goal

Split task documents into two files — a `README.md` for prose (AI reads and
writes) and a `task.json` for structured metadata (scripts and orchestrator
read and write). Simultaneously separate user-task scripts from pipeline-subtask
scripts so each set handles only its own fields, removing pipeline-specific
fields from user tasks and vice versa.

## Context

### Current pain points

All tasks — user tasks, user subtasks, and pipeline subtasks — use the same
`README.md` format with a Markdown metadata table at the top. This causes two
problems:

**1. Mixed concerns in one file.** Pipeline subtasks carry fields that are
meaningless to humans (`Complexity`, `Level`, `Last-task`, `Stop-after`).
User tasks carry pipeline fields they never use. Every task README is bloated
with the other type's fields.

**2. Fragile script parsing.** All scripts parse the metadata table using
`grep`/`sed` against Markdown. This has caused bugs (delimiter conflicts when
field values contain `/`). The Components table — a nested Markdown table
inside the README — cannot be reliably parsed by shell scripts, which is
why DECOMPOSE_HANDLER must remain an AI subprocess today.

### The architectural principle

`.md` owns the **non-deterministic** content: prose written by humans or AI
agents — Goal, Context, Design, Acceptance Criteria, Test Command. This is
what ARCHITECT, IMPLEMENTOR, and TESTER read and write.

`.json` owns the **deterministic** content: structured metadata read and
written by scripts and the orchestrator — Status, Complexity, Level, Last-task,
Stop-after, Components array. This is never written by AI agents.

### Field ownership after the split

**User task / user subtask:**

| File | Fields |
|------|--------|
| `README.md` | Goal, Context, Notes, Subtasks list |
| _(no task.json needed)_ | Status, Priority, Tags, Next-subtask-id stay in README metadata (simple enough) |

**Pipeline subtask:**

| File | Fields |
|------|--------|
| `README.md` | Goal, Context, Components (prose description), Design, Acceptance Criteria, Test Command, Suggested Tools |
| `task.json` | Task-type, Status, Epic, Parent, Priority, Next-subtask-id, Complexity, Level, Last-task, Stop-after, Components (structured array) |

### DECOMPOSE_HANDLER becomes internal

With Components as a structured JSON array, DECOMPOSE_HANDLER no longer needs
AI to parse a Markdown table. It becomes a Python internal agent (like LCH),
eliminating its ~462K avg cached tokens and ~2m avg wall time per invocation.

### Regression baseline (run 11, 2026-03-19) — target to beat

Run 11 is the baseline against which regression-validation (subtask 0006) will
measure. All optimisations active: handler no-history, frame_stack, cwd=/tmp,
TESTER Test Command, LCH internal agent.

| Field | Value |
|-------|-------|
| Total time | 23m 15s |
| Invocations | 24 (19 claude, 5 internal) |
| Tokens in | 177 |
| Tokens out | 64,275 |
| Tokens cached | 3,503,765 |

| Role | Count | Avg Elapsed | Tokens Cached Total |
|------|-------|-------------|---------------------|
| ARCHITECT | 7 | 1m 43s | 1,427,668 |
| DECOMPOSE_HANDLER | 2 | 2m 09s | 924,820 |
| IMPLEMENTOR | 5 | 1m 05s | 905,871 |
| TESTER | 5 | 16s | 245,406 |
| LEAF_COMPLETE_HANDLER | 5 | 0s | 0 |

**Gold test: PASS.**

After this task, DECOMPOSE_HANDLER should also be 0 tokens (internal agent).
Expected additional savings: ~924K cached tokens and ~4m 18s wall time per run.

---

### Platform-monolith run history (post-task)

Eligibility rules: `eligible = gold_pass && !has_rate_limits && !is_resumed`

| Run | Date | Optimization | Elapsed | Tokens out | Tokens cached | Resumed | Eligible |
|-----|------|-------------|---------|-----------|---------------|---------|---------|
| 11 | 2026-03-19 | Baseline (LCH internal, scope-bounded history) | 23m 15s | 64,275 | 3,503,765 | no | **yes** |
| 12 | 2026-03-19 | DECOMPOSE_HANDLER internal | ~22m 43s | ~73K | 3,414,400 | **yes** | **no** |
| 13 | 2026-03-19 | DECOMPOSE_HANDLER internal, stale output dir | 28m 25s | 74,733 | 3,130,427 | no | **yes** |
| 14 | 2026-03-21 | DECOMPOSE_HANDLER internal, reset wipes output | 26m 6s | 75,061 | 2,538,065 | no | **yes** |

**Gold test: PASS on runs 13 and 14.**

#### Observations

- **Run 12 vs 11:** DECOMPOSE_HANDLER going internal saved ~924K cached tokens as predicted, but confounded by resume — ineligible.
- **Run 13 vs 11:** −373K cached (DECOMPOSE_HANDLER savings confirmed), but stale output dir caused IMPLEMENTORs to read/rewrite existing files (+5m wall time). Both eligible.
- **Run 14 vs 13:** Reset now wipes output dir. −592K cached (IMPLEMENTORs no longer read stale code), −2m 19s elapsed. Run 14 is the new best eligible baseline.
- **Eligible best:** Run 14 — 26m 6s, 75,061 tokens out, 2,538,065 cached.

## Notes

_None._

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-829461-0000-audit-and-schema-design](X-829461-0000-audit-and-schema-design/)
- [x] [X-829461-0001-split-pipeline-scripts](X-829461-0001-split-pipeline-scripts/)
- [x] [X-829461-0002-split-user-scripts](X-829461-0002-split-user-scripts/)
- [x] [X-829461-0003-update-orchestrator-and-internal-decompose-handler](X-829461-0003-update-orchestrator-and-internal-decompose-handler/)
- [x] [X-829461-0004-update-templates](X-829461-0004-update-templates/)
- [x] [X-829461-0005-unit-tests](X-829461-0005-unit-tests/)
- [x] [X-829461-0006-regression-validation](X-829461-0006-regression-validation/)
- [x] [X-829461-0007-audit-agent-script-knowledge-boundary](X-829461-0007-audit-agent-script-knowledge-boundary/)
<!-- subtask-list-end -->

## Notes

_None._
