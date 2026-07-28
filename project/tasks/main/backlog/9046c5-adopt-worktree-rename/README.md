# Task: adopt-worktree-rename

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status      | backlog             |
| Epic        | main               |
| Tags        | —               |
| Priority    | MED           |
| Category    | task-tooling           |
| Created     | 2026-07-28            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Adopt the `Category` → `Worktree` rename from create-project-system v0.2.0.
Rewrite this repo's **live** task files (draft + backlog + in-progress), rename
`classes.md` → `worktrees.md`, and fix the `--category` wording in `CLAUDE.md`.

## Context

create-project-system renamed the task metadata field `Category` to `Worktree`
(its task 19, resolved 2026-07-28, commit `aa757cf`). The field never meant
"category" — it names which files a task touches, so unrelated work can run in
parallel branches. The old name kept pulling operators toward it when they
wanted **topical** grouping, which is what `Tags` is for. That misread happened
for real in `captains-log` on 2026-07-26.

**Nothing here is broken.** The generated scripts read both spellings
permanently, by design: the metadata row and `classes.md` are *content*, which
the generator never rewrites, so old spellings are not transitional state a
migration could drain. This was verified — both of this repo's bats suites pass
**unmodified** against the v0.2.0 machinery over this repo's real `classes.md`
and its legacy `| Category |` rows:

- `tests/unit/shell/test_list_tasks.bats` — 9/9
- `tests/unit/shell/test_new_user_task.bats` — 11/11

So this task is about **not letting the old vocabulary outlive the rename**, not
about restoring function. The principle: *migrate what teaches, not what merely
stores.*

### Current state

| Where | Count | Action |
|---|---|---|
| `project/tasks/main/draft/` | 12 | **rewrite** |
| `project/tasks/main/backlog/` | 45 | **rewrite** |
| `project/tasks/main/in-progress/` | 5 | **rewrite** |
| **live total** | **62** | |
| `project/tasks/main/complete/` | 13 | leave — historical record |
| `project/tasks/main/inbox/`, `wont-do/` | 0 | nothing there |
| `project/tasks/classes.md` | 8 branches | rename file |
| `CLAUDE.md` | 8 references | rewrite wording |

`CLAUDE.md` is the highest-leverage item. It is hand-written, so regeneration
will never touch it, and it currently teaches agents the old name — e.g. line
46, "Use `--category <branch>` to filter to a single worktree class". Leaving it
is how the confusion survives the rename.

## Sequencing

Best done **with or after** `15d940-target-setup-uses-generator-for-tasks`,
which bumps the vendored create-project-system pin. Until that pin moves to
v0.2.0, this repo's installed scripts are still the pre-rename copies and the
`--worktree` flag will not exist locally. One commit that moves the pin, the
file name, and the wording together keeps the change legible.

## Steps

- [ ] Bump the vendored create-project-system pin to v0.2.0 (or confirm
      `15d940` already did) and regenerate the task layer. Verify the emitted
      `new-user-task.sh` accepts `--worktree`.
- [ ] `git mv project/tasks/classes.md project/tasks/worktrees.md`. This also
      silences the generator's "pre-rename name — rename it by hand to finish
      the move" line on every regeneration. No content edit needed: the
      `**Worktree branch:**` labels inside it were already correct.
- [ ] Rewrite the metadata row `| Category |` → `| Worktree |` across all live
      task READMEs — **draft (12)**, **backlog (45)**, **in-progress (5)**.
      Mechanical: `perl -0pi -e 's{^\| Category}{| Worktree}m'` over those three
      trees. Confirm the count changed is **62**, and that no `complete/` file
      moved.
- [ ] Update `CLAUDE.md`: `--category` → `--worktree`,
      `--group-by-category` → `--group-by-worktree`, `classes.md` →
      `worktrees.md` (lines ~44, 46, 312, 313, 315, 316, 400, 411). While
      there, state the distinction explicitly — `Worktree` is parallel-work
      isolation, `Tags` is subject matter — so an agent reading only this file
      cannot repeat the original mistake.
- [ ] Rename the bats test cases that say `--category` in their titles. They
      already pass either way; this is cosmetic and can ride along.
- [ ] Run the full test suite. Expect no behavioral change.

## Scope note

`draft/` is included deliberately. Draft tasks are live work that will move to
backlog later, so excluding them just means the old row arrives there anyway.
`complete/` stays untouched: it is the historical record, and the readers handle
it correctly forever.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

- `--category` and `--group-by-category` still work at runtime after the pin
  bump; they warn on stderr and behave identically. So a missed reference
  degrades to a nudge, not a failure.
- create-project-system also shipped `set-field.sh` in the same release. It
  sets `Tags` and `Priority` on an **existing** task, which previously required
  hand-editing the metadata table or delete-and-recreate. That is the actual
  fix for the misuse — the correct tool is now as reachable as the wrong one.
  Worth mentioning in `CLAUDE.md` alongside the wording fix.
- `set-field.sh` deliberately does **not** set `Worktree` yet. An operator who
  mis-assigns a worktree still has no scripted way to correct it; that gap is
  recorded upstream in create-project-system task 19.
