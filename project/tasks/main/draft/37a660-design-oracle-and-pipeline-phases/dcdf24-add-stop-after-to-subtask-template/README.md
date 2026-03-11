# Subtask: add-stop-after-to-subtask-template

| Field    | Value                |
|----------|----------------------|
| Status   | —                    |
| Epic     | main             |
| Tags     | oracle, tooling             |
| Parent   | 37a660-design-oracle-and-pipeline-phases           |
| Priority | MED         |

## Description

Add a `Stop-after` field to `project/tasks/scripts/subtask-template.md` and
update the corresponding copies in `target/project/tasks/scripts/`.

The `Stop-after` field marks a phase boundary — when `true`, the Oracle pauses
the implementation loop after this subtask completes and surfaces results to
the human for review before continuing.

**Changes:**

- Add `| Stop-after | false |` to the metadata table in `subtask-template.md`
  (default: `false`)
- Mirror the same change in `target/project/tasks/scripts/subtask-template.md`
- Update `project/tasks/README.md` and `target/project/tasks/README.md` to
  document the field and its semantics
- Update `CLAUDE.md` with a note that the PM should set `Stop-after: true`
  on subtasks that produce public interfaces, introduce dependencies, or
  are flagged as review checkpoints during discovery

## Notes

**`Stop-after` is an exception, not the default.** The pipeline should
continue automatically to IMPLEMENTOR in the common case. Human review via
`project/reviews/` happens after the fact for most jobs. `Stop-after: true`
is reserved for situations where the architectural risk is high enough that
a human must validate the plan before expensive implementation begins.

`Stop-after: true` triggers (exceptional cases):
- Jobs spanning many directories or introducing major new abstraction layers
- Architectural decisions that are irreversible or expensive to undo
- Requests ambiguous enough that the ARCHITECT's interpretation needs
  human validation before work begins
- Public interfaces (API, CLI, library surface) where a wrong design
  costs significantly more to fix post-implementation

`Stop-after: false` (default — the common case):
- Internal helpers, utilities, pure refactors
- Test files accompanying an already-reviewed implementation
- Well-scoped jobs where the ARCHITECT's plan is low-risk
- Jobs within a well-established area of the codebase

The ARCHITECT (not the PM) should set `Stop-after: true` when it judges
the complexity warrants it. The PM should not set it by default.
