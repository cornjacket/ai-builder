# Task: doc-architect-prompt

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | b9529c-doc-pipeline             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Write `machines/doc/roles/DOC_ARCHITECT.md` — the role prompt for DOC_ARCHITECT.
Must handle two modes detected from the task at hand: decompose (directory has
subdirs) and atomic (leaf directory, source files only).

## Context

**Decompose mode:**
- Scan the directory; identify subdirectories as sub-components
- Identify parent-level source files (live alongside subdirs)
- Decide what to skip: `*_test.go`, generated files, `vendor/`, mocks
- Return components JSON + one `integrate` entry last
- Do NOT write any docs — decompose is a pure planning step
- Emit DOC_ARCHITECT_DECOMPOSITION_READY

**Atomic mode:**
- Read all source files in the directory (check for existing .md files first)
- Write companion `.md` files and `README.md` directly
- Distinguish: complete doc (preserve), missing doc (create), stale doc (update)
- Emit DOC_ARCHITECT_ATOMIC_DONE with compact handoff summary of what was produced

Purpose/Tags header required on every .md file written (see docs/guidelines/doc-format.md).
DOC_ARCHITECT has no integrate mode — the integrate subtask routes directly to
DOC_INTEGRATOR via LCH route_on.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
