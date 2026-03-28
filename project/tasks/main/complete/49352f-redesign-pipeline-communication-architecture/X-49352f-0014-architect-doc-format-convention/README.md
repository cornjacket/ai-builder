# Task: architect-doc-format-convention

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

Update the ARCHITECT role prompt to instruct when and how to write design
documentation files, and define the shared doc format convention
(Purpose:/Tags: header block) that both ARCHITECT and IMPLEMENTOR must follow.
Create `roles/doc-format.md` as the authoritative format spec, then reference
it from both `roles/ARCHITECT.md` and `roles/IMPLEMENTOR.md`.

## Context

DOCUMENTER (subtask 0012) is wired in and ready to index `.md` files, but
neither producer (ARCHITECT nor IMPLEMENTOR) has been told to produce them in
the required format. DOCUMENTER scans for a `Purpose:` first sentence and a
`Tags:` field — if these aren't present the index will be empty.

**Doc format convention:**
Each `.md` doc written to the output directory must begin with a header block:

```
Purpose: One standalone sentence describing what this file covers.
Additional context sentence(s) if needed (2-3 sentences total max).

Tags: <tag1>, <tag2>, ...
```

The first sentence of `Purpose:` must stand alone as a complete description
(DOCUMENTER uses it as the index entry). Tags must include the role that wrote
the doc (`architecture`, `design`, or `implementation`) and the component name.

**ARCHITECT doc-writing rules to add to `roles/ARCHITECT.md`:**
- In decompose mode: write one design doc per major architectural decision
  (data flow, component boundaries, shared contracts). Set `documents_written: true`.
- In atomic (design) mode: write docs only for non-trivial components
  (skip for `integrate` and simple wrappers). Set `documents_written: false`
  for trivial components.
- All ARCHITECT docs: `Tags: architecture, design` (no `implementation` tag).

**Deliverables:**
1. `roles/doc-format.md` — the format spec (Purpose:/Tags: block, when to write,
   what belongs in each section)
2. Update `roles/ARCHITECT.md` — add doc-writing instructions and reference
   `doc-format.md`
3. Update `roles/IMPLEMENTOR.md` — add format reference (0013 handles the rest)

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
