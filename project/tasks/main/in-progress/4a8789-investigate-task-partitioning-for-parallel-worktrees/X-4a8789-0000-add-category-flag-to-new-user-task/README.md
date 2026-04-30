# Task: add-category-flag-to-new-user-task

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 4a8789-investigate-task-partitioning-for-parallel-worktrees             |
| Priority    | —           |
| Created     | 2026-04-30            |
| Completed | 2026-04-30 |
| Next-subtask-id | 0000               |

## Goal

Add a `--category` flag to `project/tasks/scripts/new-user-task.sh` so the
worktree class is set at creation time rather than left as `—` for the
operator to backfill manually.

## Context

The CLAUDE.md rule (`## Task Management`, the `Category:` rule) requires every
USER-TASK to have a populated `Category:` field, set to a branch name from
[`project/tasks/classes.md`](../../../../../../project/tasks/classes.md) (or
`unclassified` if no class fits). Today, `user-task-template.md` hardcodes
`Category | —`, and the script has no way to override it — so every newly
created task starts in violation of the rule and depends on the operator to
remember to `Edit` the README.

**Scope:**

- Add `--category <name>` to `new-user-task.sh`, mirroring how `--priority`
  works (substitution into the template via `sed`).
- Validate against the class list parsed from `project/tasks/classes.md` (the
  `**Worktree branch:** <name>` lines), plus the special value `unclassified`.
  Reject unknown values with a clear error and a list of valid options.
- Make the flag **required** for `new-user-task.sh` (subtasks/pipeline tasks
  don't need it — only USER-TASKs do per the rule). Update the usage banner
  and examples.
- Update `project/tasks/README.md` examples and the CLAUDE.md ### Scripts
  block to show `--category`.
- Add a test task to verify the flag works end-to-end (per CLAUDE.md "test
  task" rule), then move it to `complete/` rather than deleting.

**Out of scope:**

- Backfilling existing tasks that have `Category: —`. That's a separate audit
  task (see Notes).
- Adding `--category` to `new-user-subtask.sh` / pipeline scripts (subtasks
  inherit context from the parent USER-TASK).

## Notes

Related follow-up: an audit pass to fix any USER-TASKs in `backlog/` /
`in-progress/` that still have `Category: —` (a few were spotted during
4a8789 analysis, e.g. `59d31e-add-completion-summary-to-target-claude-md`).

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
