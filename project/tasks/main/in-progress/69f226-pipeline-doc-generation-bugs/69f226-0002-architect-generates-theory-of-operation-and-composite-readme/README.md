# Task: architect-generates-theory-of-operation-and-composite-readme

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 69f226-pipeline-doc-generation-bugs             |
| Priority    | —           |
| Next-subtask-id | 0000               |

## Goal

Update the ARCHITECT decompose/composite prompt so that at every composite source
level it creates (a directory containing child component directories), it produces:

1. **`theory-of-operation.md`** — explains the data-flow at this level. Must include
   at least one of: ASCII block diagram, decision tree, or state machine. Tagged
   `architecture, design`.

2. **`README.md`** — composite-level overview containing:
   - `Purpose:` / `Tags:` header
   - A description of the design at this level
   - A table listing each child component directory with its purpose and a link to
     its `README.md` (links are written even if the child README does not yet exist)
   - A link to `theory-of-operation.md`

## Context

Currently the ARCHITECT only creates documentation at leaf component level. Intermediate
composite directories (e.g. `internal/userservice/`) have no README or theory-of-operation.
This breaks navigability — there is no README chain from the output root down to leaf
components.

**What "architecturally/functionally relevant" means:**
A directory is relevant if it represents a named design boundary — a package, module,
or layer the ARCHITECT consciously chose to create. Scaffolding directories that exist
only due to language convention (`internal/`) are not relevant; the first meaningful
directory below them is.

**Scope:** Update `roles/ARCHITECT.md` (the decompose-mode instructions). The change
must not leak into the agent knowledge boundary — no orchestrator internals in the prompt.

After this subtask, running a fresh regression should produce the missing READMEs,
allowing the gold tests from 0001 to pass.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
