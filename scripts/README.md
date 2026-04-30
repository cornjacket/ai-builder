# Scripts

General-purpose repo scripts that operate on the working tree at the repo
root level. Distinct from:

- [`bootstrap/`](../bootstrap/) — workspace and worktree setup scripts
- [`project/tasks/scripts/`](../project/tasks/scripts/) — task management scripts

## Scripts

### `log-add.sh`

Appends an entry to [`log.md`](../log.md), or back-fills the most recent
`_pending_` hash with the current short HEAD. Writes `log.md` only — does
not commit.

See [`log-add.md`](log-add.md) for full usage and the surrounding workflow.
The convention this script supports is documented in the
[Work Log](../CLAUDE.md#work-log) section of `CLAUDE.md`.
