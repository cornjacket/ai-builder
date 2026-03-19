# Task: split-task-format-md-json-and-scripts

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | in-progress |
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

## Notes

_None._

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-829461-0000-audit-and-schema-design](X-829461-0000-audit-and-schema-design/)
- [ ] [829461-0001-split-pipeline-scripts](829461-0001-split-pipeline-scripts/)
- [ ] [829461-0002-split-user-scripts](829461-0002-split-user-scripts/)
- [ ] [829461-0003-update-orchestrator-and-internal-decompose-handler](829461-0003-update-orchestrator-and-internal-decompose-handler/)
- [ ] [829461-0004-update-templates](829461-0004-update-templates/)
- [ ] [829461-0005-unit-tests](829461-0005-unit-tests/)
- [ ] [829461-0006-regression-validation](829461-0006-regression-validation/)
- [ ] [829461-0007-audit-agent-script-knowledge-boundary](829461-0007-audit-agent-script-knowledge-boundary/)
<!-- subtask-list-end -->

## Notes

_None._
