# Task: verify-output-doc-headers

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

Confirm that every `.md` file written to the output directory by pipeline
agents (ARCHITECT, IMPLEMENTOR) has a valid `Purpose:` / `Tags:` header
block as defined in `roles/doc-format.md`. Fix any agents or prompts that
produce non-conforming docs.

## Context

`build_master_index.py` silently skips files with no `Purpose:` / `Tags:`
header — so missing headers cause silent gaps in the index. The header
convention is defined in `roles/doc-format.md` and required by `ARCHITECT.md`,
but it is not yet verified automatically.

**What to check:**
1. Run a regression (or inspect an existing output directory) and collect all
   `.md` files not named `README.md` or `master-index.md`.
2. For each file, verify it starts with a `Purpose:` line followed by a
   `Tags:` line.
3. Trace any missing headers back to the responsible agent prompt
   (`ARCHITECT.md`, `IMPLEMENTOR.md`) and add or tighten the instruction.

**Also check README.md files:** ARCHITECT writes `README.md` to the output
(source package) directory. Confirm those README.md files also carry the
`Purpose:` / `Tags:` header so they can be indexed if the exclusion rule is
ever relaxed.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
