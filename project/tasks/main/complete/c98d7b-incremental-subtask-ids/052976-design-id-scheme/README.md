# Task: design-id-scheme

| Field       | Value                       |
|-------------|------------------------------|
| Task-type   | USER-SUBTASK                 |
| Status | complete |
| Epic        | main                         |
| Tags        | —                            |
| Parent      | c98d7b-incremental-subtask-ids |
| Priority    | —                            |

## Goal

Nail down all design decisions before any code changes:

1. **Metadata field name and format** — confirm `Next-subtask-id: 0000` (zero-padded 4 digits); determine where it lives in the table
2. **ID derivation** — how `new-user-subtask.sh` extracts the parent's short ID from the directory name (e.g. strip everything after the first `-` in the basename? or read a field?)
3. **X-prefix behavior** — confirm `X-` is prepended to the full directory name on complete; decide how `list-tasks.sh` and lookup scripts detect and strip it
4. **Backward compatibility** — existing tasks with hash-prefixed subtasks; scripts must handle both old (hash-prefix) and new (incremental) formats during transition
5. **Script interface changes** — list any flag changes or new scripts needed

Document decisions as notes in this README, then get Oracle sign-off before implementation begins.

## Subtasks

<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

### Decision 1 — Metadata field

Field name: `Next-subtask-id`
Format: zero-padded 4-digit integer string, e.g. `0000`, `0001`, `0042`
Location: after `Priority` in the metadata table
Initial value: `0000` in all templates

### Decision 2 — ID derivation

The parent's short ID is the portion of its directory basename **before the
first `-`** that is followed by the rest of the name. All top-level task
directories are `{6-char-hex}-{name}`, so `basename | cut -d'-' -f1` yields
the 6-char prefix reliably.

For subtask-of-subtask (nested), the parent is e.g.
`c98d7b-0002-update-scripts` — the short ID is still `c98d7b` (first
segment). This keeps all IDs in a tree rooted at the top-level task ID,
making the hierarchy traceable from any directory name.

New subtask directory name: `{parent-short-id}-{NNNN}-{name}`
Example: `c98d7b-0003-update-complete-script`

### Decision 3 — X-prefix on completion

`complete-task.sh --parent` renames the subtask directory:
`c98d7b-0001-update-templates` → `X-c98d7b-0001-update-templates`

The parent README subtask list link is also updated to match the new path.

`list-tasks.sh` already skips `[x]` entries when `--all` is not set, so
`X-` prefixed directories will naturally not appear in normal output.
When `--all` is passed, `X-` directories are shown as-is.

Scripts that look up a subtask by name (e.g. `complete-task.sh`,
`show-task.sh`) must search for both `{name}` and `X-{name}` forms.

### Decision 4 — Backward compatibility

Existing tasks with hash-prefixed subtask directories are **not renamed** —
migration is handled by a dedicated subtask (`8087e2-migrate-existing-subtask-ids`).
During the transition period, all scripts must handle both naming schemes:
- Old: `{6-char-hex}-{name}` (e.g. `d05f90-split-task-manager`)
- New: `{parent-id}-{NNNN}-{name}` (e.g. `c98d7b-0002-update-scripts`)

There is no ambiguity: old names have a 6-char hex segment followed
directly by a name; new names have a 6-char hex segment, then a 4-digit
decimal segment, then a name. Scripts can detect the format by checking
whether the second `-`-delimited segment is all digits.

### Decision 5 — Script interface changes

No new flags required. Changes are internal to existing scripts:
- `new-user-subtask.sh` and `new-pipeline-subtask.sh`: replace
  `openssl rand -hex 3` with read/increment of `Next-subtask-id`
- `complete-task.sh --parent`: add directory rename + README link update
- `list-tasks.sh`, `show-task.sh`, `move-task.sh`, etc.: handle `X-` prefix
  in directory lookups and display

A shared helper file `task-id-helpers.sh` will contain:
- `get_next_subtask_id <parent-readme>` — reads the field value
- `increment_subtask_id <parent-readme>` — writes the incremented value
- `get_parent_short_id <parent-dir>` — extracts first segment of basename
