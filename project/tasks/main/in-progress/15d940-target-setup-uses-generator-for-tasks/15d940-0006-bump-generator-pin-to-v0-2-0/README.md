# Task: bump-generator-pin-to-v0-2-0

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | 15d940-target-setup-uses-generator-for-tasks             |
| Priority    | —           |
| Created     | 2026-08-07            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Move the vendored create-project-system snapshot from `v0.1.0` to `v0.2.0`, and
retire the "stay on v0.1.0" hold that subtask 0000 wrote into `vendor/README.md`.
Re-vendor `generate.sh` + `src/`, update `PIN` (tag, sha, manifest-sha256), and
correct the layer-1 contract text that `vendor/README.md` and `PIN` both state.

Inserted ahead of the sandbox install regression deliberately: the regression
should exercise the version this repo intends to ship, not validate v0.1.0 and
then need a second run after the bump.

## Context

Subtask 0000 pinned at `v0.1.0` (`c003956`) and set an explicit release
condition: *stay on v0.1.0 until upstream cuts a tag that states a migration
position.* `v0.2.0` (`322924c`, cut 2026-08-03) states one:

> NO MIGRATION IS REQUIRED. This is the property to rely on when bumping a pin.

**The ~134-row metadata migration this task feared does not exist.** The rename
splits along the generator's own machinery/content line. Flags, scripts,
templates and docs are machinery — always overwritten, so the rename propagates
on regeneration at zero cost. Metadata rows in existing task READMEs, and
`classes.md`, are *content*, which the generator never rewrites. Old spellings
are therefore permanent state, not transitional state a migration could drain,
and the readers accept both permanently by design:

- `list-tasks.sh` reads `| Worktree |`, falling back to `| Category |`; a repo
  may hold a mix indefinitely and still filter and group correctly.
- Both scripts read `worktrees.md`, falling back to `classes.md`.
- `generate.sh` seeds `worktrees.md` only when *neither* name exists — even
  under `--force` — so regenerating over a pre-rename install never leaves an
  empty starter shadowing real definitions.
- Runtime `--category` / `--group-by-category` warn on stderr and still work.

### The one breaking change does not touch this repo's call site

`--with-classes` → `--with-worktrees`, and the old flag now exits non-zero
rather than aliasing (generate-time flags are typed once, during a deliberate
upgrade, so upstream chose to error rather than silently accept). But
`setup-project.sh:171-178` passes eight flags —

```
--target-repo --tasks-dir --epic --with-status --with-skill
--inject-claude-md --with-projects --with-worktree-guard
```

— and `--with-classes` is **not** among them. All eight still exist in the
v0.2.0 parser (verified against `generate.sh:60-78` at that ref). **No
`setup-project.sh` edit is required by this bump.**

The other blocker `vendor/README.md` names, task 15's `--require-category`, is
not in this tag; upstream defers it to a later release. It stays a future
concern.

### Verified upstream, against this repo

v0.2.0's notes report create-ai-builder's own bats suites passing **unmodified**
against the new machinery over this repo's real `classes.md` and its legacy
`| Category |` rows — `test_list_tasks.bats` 9/9, `test_new_user_task.bats`
11/11. Re-run them here rather than trusting the note.

### Pre-bump state

The vendored snapshot is clean: the recorded `manifest-sha256`
(`17e9612a555eb1c73568a3e700468f6accfa5d930d811e2c04aa43b6d0f3589c`) recomputes
exactly, so nothing has drifted or been hand-edited. The bump starts from a
known-good base.

### Scope boundary

This subtask moves **the pin only**. Adopting the new vocabulary inside *this*
repo — `classes.md` → `worktrees.md`, the 62 live task metadata rows, the eight
`CLAUDE.md` references — belongs to backlog task
`9046c5-adopt-worktree-rename`, which already sequences itself "with or after"
this parent task and whose first step is to confirm this bump happened. Do not
absorb that work here.

## Steps

- [ ] Re-vendor at v0.2.0 per the procedure in `vendor/README.md`:
      `git -C <cps> archive v0.2.0 generate.sh src | tar -x`, `chmod +x generate.sh`.
- [ ] Recompute `manifest-sha256` and update `PIN` — tag `v0.2.0`, sha
      `322924c4b58d15b9815b8dabb0471f2773a89d53`, new manifest.
- [ ] Update the flag contract recorded in `PIN`: `--with-classes` becomes
      `--with-worktrees`. Still ten flags, still no `--with-pipeline`.
- [ ] Update `vendor/README.md`: the pin table, the v0.1.0 contract block, and
      the "Bumping the pin" section — whose "stay on v0.1.0" instruction and its
      stated migration fear are both retired by this bump. Replace with what the
      *next* bump should watch for (task 15 / `--require-worktree`).
- [ ] Run the repo's bats suites; expect no behavioral change.
- [ ] Leave the sandbox install regression to subtask 0007.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

`insert-subtask.sh` emitted two defects while creating this subtask, both
cosmetic and both worth folding into `23450c-unit-test-task-management-scripts`:
the `Created` field was left as the literal `{{CREATED}}` placeholder (fixed by
hand here), and `Next-subtask-id` was bumped `0008 → 0010` when the highest
position after the shift is `0008`, so `0009` was correct.
