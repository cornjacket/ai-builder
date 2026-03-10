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

`Stop-after: true` guidelines (for documentation):
- Public interfaces (API, CLI, library surface)
- New dependencies or build system changes
- Major architectural component boundaries
- Subtasks flagged as review checkpoints during the Discovery phase

`Stop-after: false` (default) for:
- Internal helpers, utilities, pure refactors
- Test files accompanying an already-reviewed implementation
