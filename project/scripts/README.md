# project/scripts

Cross-cutting process scripts that operate on repo-level artifacts. These
scripts don't belong to a single subsystem inside `project/` — they support
the repo's overall development process.

Distinct from:

- [`../../bootstrap/`](../../bootstrap/) — workspace and worktree setup scripts
- [`../tasks/scripts/`](../tasks/scripts/) — task management scripts

## Scripts

### `log-add.sh`

Appends an entry to the repo-root [`log.md`](../../log.md), or back-fills the
most recent `_pending_` hash with the current short HEAD. Writes `log.md`
only — does not commit.

See [`log-add.md`](log-add.md) for full usage and the surrounding workflow.
The convention this script supports is documented in the
[Work Log](../../CLAUDE.md#work-log) section of `CLAUDE.md`.
