# Task: investigate-output-documentation-quality

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 49352f-redesign-pipeline-communication-architecture             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Investigate why pipeline-generated output documentation is a single
over-stuffed `README.md` rather than purpose-named files (`data-flow.md`,
`api.md`, `models.md`, etc.), and why source code files have no `Purpose:`/
`Tags:` header block. Identify the root cause in the agent prompts and produce
fixes.

## Context

Inspecting the platform-monolith output reveals two problems:

**Problem 1 — Monolithic README instead of named docs**

Every component's documentation ends up in a single `README.md`. The intended
model (per `roles/doc-format.md` and `ARCHITECT.md`) is that `README.md` is
the *entry point* — a file index and overview — while detail topics live in
named companion files: `data-flow.md`, `api.md`, `models.md`,
`locking-strategy.md`, etc. The current output collapses everything into
README, making it verbose and hard to navigate.

Likely causes to investigate:
- ARCHITECT prompt says "write a README.md" but gives no instruction to split
  topics into named files unless they "overflow the README" — this threshold
  is vague and agents default to the single-file path
- IMPLEMENTOR prompt may not instruct agents to write companion `.md` files
  alongside source files at all, or the instruction is too weak
- DOCUMENTER may be collapsing separate docs back into README rather than
  preserving named files

**Problem 2 — Source files have no `Purpose:`/`Tags:` header**

Go source files (`.go`) produced by IMPLEMENTOR have no header comment block.
The `Purpose:`/`Tags:` convention defined in `roles/doc-format.md` is written
for `.md` files, but source files should carry an equivalent package-level
doc comment that serves the same role for code indexing and discovery:

```go
// Purpose: Thread-safe in-memory user store.
// Tags: store, iam, lifecycle
package store
```

Neither `IMPLEMENTOR.md` nor `doc-format.md` currently specifies this
requirement for source files. `build_master_index.py` only indexes `.md`
files — source file headers would need a separate indexer or the convention
needs to be `.md`-only with IMPLEMENTOR writing a companion `store.md`
alongside `store.go`.

**Investigation steps:**
1. Read `roles/ARCHITECT.md`, `roles/IMPLEMENTOR.md`, `roles/doc-format.md`
   and identify every instruction (or gap) that influences documentation
   output format
2. Inspect actual platform-monolith output for a representative component
   (e.g. `internal/iam/lifecycle/`) — list every file produced, compare
   against what should exist
3. Determine whether the gap is a missing instruction, a vague instruction,
   or an instruction that agents are ignoring
4. Propose concrete prompt changes: explicit named-file requirements for
   ARCHITECT (e.g. "for a component with an HTTP API, write `api.md`; for
   a component with a data model, write `models.md`"), and a source file
   header convention for IMPLEMENTOR
5. Decide whether `build_master_index.py` should be extended to index source
   file headers or whether companion `.md` files are sufficient

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
