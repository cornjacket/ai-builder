# Task: move-roles-to-ai-builder-roles-builder

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 46f78a-stage-builder-machine-as-configurable-pipeline             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Create `ai-builder/docs/guidelines/`, move format/standards files there, inline
the missing `doc-format.md` rules into `ARCHITECT.md` and `IMPLEMENTOR.md`, and
retire `TESTER.md`. This subtask removes all references to `roles/doc-format.md`
from the role prompts before they are moved in subtask 0003.

## Context

### 1. Create `ai-builder/docs/guidelines/`

New files:

**`ai-builder/docs/guidelines/doc-format.md`** — moved from `roles/doc-format.md`
verbatim. No content changes.

**`ai-builder/docs/guidelines/documentation-standards.md`** — extracted from
`roles/DOCUMENTER.md`. Strip the "Role: DOCUMENTER" header, "Pipeline Position",
"What DOCUMENTER Receives", and "Scope Note" sections (these are either stale or
covered by `agents/builder/documenter.md`). Keep the full Documentation Guideline
section: every directory gets a README, every source file gets a companion `.md`,
named detail files, README vs detail file allocation, heading hierarchy, source
material hierarchy.

**`ai-builder/docs/guidelines/README.md`** — index of both files.

**`ai-builder/docs/README.md`** — top-level docs overview.

### 2. Inline missing rules into ARCHITECT.md and IMPLEMENTOR.md

`doc-format.md` contains rules the agents need but do not currently have inlined:

**Purpose field rules** (absent from both role files):
- First sentence must stand alone as a complete description
- 2–3 sentences total maximum
- Present tense: "Describes..." not "This file describes..."

**Complete markdown header block example** (absent from ARCHITECT.md):
```
Purpose: First sentence — a standalone description.
Additional context if needed.

Tags: architecture, design
```

**Tags required-values table** (implicit in IMPLEMENTOR.md, not in ARCHITECT.md):
- ARCHITECT docs: `Tags: architecture, design`
- IMPLEMENTOR docs: `Tags: implementation, <component-name>`
- Additional tags are additive; do not remove required tags

After inlining, **remove all `roles/doc-format.md` references** from both files
(5 total across ARCHITECT.md and IMPLEMENTOR.md). The files must be self-contained —
agents cannot follow file references at runtime.

### 3. Retire `roles/TESTER.md`

Delete the file. Its content is fully covered by:
- `agents/builder/tester.md` — implementation behaviour
- `agent-roles.md` — valid outcome values

### 4. Retire `roles/TASK_MANAGER.md` — inline valuable content into `CLAUDE.md`

`TASK_MANAGER.md` was an AI agent prompt for when TM was an AI agent. That role
no longer exists. The mechanical workflow is already in CLAUDE.md. Three sections
contain genuine operator guidance not yet in CLAUDE.md — inline them before deleting:

**Task granularity rules** — add to the Task Management section in CLAUDE.md:
- A top-level task should be completable in a single ARCHITECT→IMPLEMENTOR→TESTER run
- Split if IMPLEMENTOR would touch more than ~5 unrelated files or ~3 independent concerns
- A subtask should be a single, verifiable action — not a phase or theme
- When in doubt, smaller is better

**TESTER failure decision rules** — add as a new subsection in CLAUDE.md:
| Failure type | Action |
|---|---|
| Bug in code just written | Create new subtask in current task for the fix; do not widen scope |
| Requirement misunderstood | Update task description; restart ARCHITECT for this task |
| Systemic issue (missing dependency, wrong environment) | Create new blocking task; pause current task |
| Flaky test or environment noise | Retry TESTER once; if it fails again, treat as real failure |

**When to break down vs. proceed as one** — add alongside granularity rules:
- Break down: ARCHITECT cannot design without resolving an unknown first; IMPLEMENTOR
  would need to make a structural decision that warrants review; two parts are
  independently testable with no shared state
- Proceed as one: all inputs/outputs known; IMPLEMENTOR can work linearly; TESTER
  can verify in one pass

After inlining, delete `roles/TASK_MANAGER.md`.

### 5. Update `CLAUDE.md`

- Reference to `roles/DOCUMENTER.md` (lines ~67 and ~275): update to point to
  `ai-builder/docs/guidelines/documentation-standards.md`.
- Inline the three `TASK_MANAGER.md` sections described in step 4.

### Verification

```bash
# No roles/doc-format.md references remain in role prompt files
grep -rn "roles/doc-format" roles/

# roles/TESTER.md and roles/TASK_MANAGER.md are deleted
ls roles/

# CLAUDE.md no longer references roles/DOCUMENTER.md
grep -n "DOCUMENTER.md" CLAUDE.md
```

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
