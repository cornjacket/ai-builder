# Subtask: add-pipeline-fields-to-templates

| Field    | Value                |
|----------|----------------------|
| Status   | —                    |
| Epic     | main             |
| Tags     | oracle, tooling             |
| Parent   | 37a660-design-oracle-and-pipeline-phases           |
| Priority | MED         |

## Description

Add two pipeline control fields to both `task-template.md` and
`subtask-template.md` (and their copies in `target/project/tasks/scripts/`).
These fields make the PM a deterministic state machine — it reads fields
directly rather than re-asking the ARCHITECT what to do with each node.

**Field 1: `Stop-after`**

Marks a phase boundary. When `true`, the Oracle pauses the implementation
loop after this node completes and surfaces results to the human.

- Default: `false`
- Set by: ARCHITECT (not PM) when architectural risk warrants human review

**Field 2: `Complexity`**

Signals whether a node needs decomposition or can go directly to the
IMPLEMENTOR. The ARCHITECT writes this when producing a component list.
The PM reads it to decide next action — no AI re-derivation needed.

- Values: `atomic` | `composite`
- Default: `atomic`
- `atomic` → PM submits to ARCHITECT (design pass) → IMPLEMENTOR → TESTER
- `composite` → PM submits to ARCHITECT (decompose pass) → creates subtasks

**Changes:**

- Add `| Stop-after  | false  |` to both templates
- Add `| Complexity  | atomic |` to both templates
- Mirror changes in `target/project/tasks/scripts/`
- Update `project/tasks/README.md` and `target/project/tasks/README.md`
  to document both fields and their semantics

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
