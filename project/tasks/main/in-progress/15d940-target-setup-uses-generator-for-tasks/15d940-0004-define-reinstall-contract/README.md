# Task: define-reinstall-contract

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 15d940-target-setup-uses-generator-for-tasks             |
| Priority    | —           |
| Created     | 2026-07-28            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Define what re-running `setup-project.sh` against an already-installed target
does, now that layer 1 comes from a generator built to be re-runnable.

## Context

**Contract: bare re-run declines; `--upgrade` refreshes in place.**

The old guard exited early and told the operator "to reinstall, remove
`$TARGET_TASKS` first" — advice that would have deleted **every task in the
target** along with the machinery. That message is gone.

The safety is structural, not conventional. Reading the vendored generator:

- `render()` writes unconditionally — used for all machinery (scripts,
  `docs/USING.md`, `SKILL.md`, `task-config.sh`). So a re-run repairs drift.
- `seed()` writes only when the destination is absent — used for
  user-editable files (`classes.md`, `status/README.md`).
- `--inject-claude-md` replaces the block between its own
  `<!-- task-system:begin/end -->` markers rather than appending.
- Task content under `project/tasks/<epic>/` is not written by any path.

So re-running *without* `--force` is exactly a safe upgrade, which is why
`--upgrade` maps to it directly.

**`--force` deliberately not exposed.** Its only effect is to re-seed
user-editable files — i.e. to overwrite a target's hand-edited `classes.md`
and status README. Nothing about bumping a pin needs that. If it is ever
wanted it should be a separate, louder flag, not a passthrough.

`--upgrade` on a directory that was never installed into is rejected rather
than silently treated as a fresh install, so a typo'd path cannot quietly
provision a new repo.

**Verified on a sandbox target**, against a deliberately dirtied install —
a drifted machinery script, a hand-edited seeded file, hand-written CLAUDE.md
prose outside the block, and a real task with edited content:

- task directory and its README edits survive
- `status/README.md` edit survives
- hand-written CLAUDE.md section survives, block count stays 1
- the drifted `list-tasks.sh` is restored
- the 7-script pipeline overlay is re-applied (35 scripts after upgrade)

Coverage added to `tests/regression/template-setup/test.sh` as section 2b,
including the never-installed rejection and an assertion that the rejection
installs nothing.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
