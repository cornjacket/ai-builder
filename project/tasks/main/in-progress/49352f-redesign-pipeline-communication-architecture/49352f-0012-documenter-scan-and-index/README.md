# Task: documenter-scan-and-index

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 49352f-redesign-pipeline-communication-architecture             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Implement DOCUMENTER as an internal Python handler (not an AI agent) that scans
the component's output directory for `*.md` files, extracts their `Purpose:`
first sentence and `Tags:` field, and rebuilds `README.md` with a two-section
index: Design (no `implementation` tag) then Implementation Notes (`implementation`
tag). DOCUMENTER runs after ARCHITECT and conditionally after IMPLEMENTOR.

## Context

Currently DOCUMENTER is not yet implemented in the pipeline. The redesigned
pipeline introduces it as a deterministic internal handler — no AI needed for
scanning files and building an index table.

**Trigger conditions:**
- After ARCHITECT (atomic mode): always runs if `documents_written: true`
- After IMPLEMENTOR: runs if `documents_written: true`

**Scan logic:**
1. Find all `*.md` files in the component output directory, excluding `README.md`
2. For each file, extract:
   - `Purpose:` — first sentence of the `Purpose:` section (one-liner description)
   - `Tags:` — comma-separated tag list
3. Split into two buckets: files without `implementation` tag (design docs), files
   with `implementation` tag (implementation notes)

**README.md output:**
```markdown
## Documentation

### Design
| File | Description |
|------|-------------|
| data-flow.md | How requests flow from handler through store... |

### Implementation Notes
| File | Description |
|------|-------------|
| store.md | Non-obvious locking strategy for concurrent deletes... |
```
Omit the Implementation Notes section entirely if no implementation docs exist.

**Tag convention (enforced by role prompts):**
- ARCHITECT docs: `Tags: architecture, design` — no `implementation` tag
- IMPLEMENTOR docs: `Tags: implementation, <component-name>`
- Additional tags are additive

DOCUMENTER **rebuilds README.md from scratch each time** — ARCHITECT docs and
IMPLEMENTOR docs are both captured correctly regardless of which ran last.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
