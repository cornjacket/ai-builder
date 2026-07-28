# Task: delegate-layer-1-to-generate

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status | complete |
| Epic        | main               |
| Tags        | —               |
| Parent      | 15d940-target-setup-uses-generator-for-tasks             |
| Priority    | —           |
| Created     | 2026-07-28            |
| Completed | 2026-07-28 |
| Next-subtask-id | 0000               |

## Goal

Rewrite the layer-1 half of `target/setup-project.sh` to delegate to the pinned
`vendor/create-project-system/generate.sh`, removing the copy-of-a-copy and the
hand-rolled epic scaffolding.

## Context

Removed: the `cp -r target/project` skeleton copy, the `cp -r` of this repo's
own `project/tasks/scripts/`, the hand-rolled epic folder creation, and the
"remove main/ if a different epic was requested" cleanup (the generator only
creates the epic it is asked for).

Generator flags chosen: `--with-status --with-skill --inject-claude-md
--with-projects --with-worktree-guard`. The design doc's checklist names only
the first three; `--with-projects` and `--with-worktree-guard` are needed for
**parity** with what targets get today (`new-project.sh`, `list-projects.sh`,
`check-task-complete.py` are all in the canonical script set).

`--with-classes` deliberately omitted — targets do not get a `classes.md`
today, and the flag only seeds a starter file that would not carry this repo's
worktree classes across anyway. Adding it is a scope expansion, not parity.

**Layer split confirmed empirically**, not assumed: diffing the generated
script set against this repo's canonical 35 gives an exact partition —
28 generated + 7 pipeline (`advance-pipeline`, `check-stop-after`,
`new-pipeline-build`, `new-pipeline-subtask`, `on-task-complete`,
`set-current-job`, `pipeline-build-template.md`), matching the design doc's
list with nothing left over.

Those 7 are installed here as an explicit named seam so the branch never has a
commit where targets lose the pipeline;
`15d940-0002-pipeline-overlay-layer-2` fleshes it out with orchestrator, roles
and machines.

Verified on a sandbox target: install reproduces the canonical 35 scripts
exactly (no missing, no extra), all four layer-1 checklist items land, and the
two layers interoperate — hand-owned `new-pipeline-build.sh` reads the
*generated* `task-config.sh` and creates a pipeline subtask with `task.json`
under a layer-1-created user task, unmodified.

Deliberately left alone (owned by later subtasks): the hard-exit idempotency
guard (0004), `init-claude-md.sh` and the SETUP.md steps referencing it (0003),
`verify-setup.sh` (0005 — already stale, it checks a `task-template.md` that
no longer exists). `target/project/tasks/README.md` is kept for now: it is
layer-2 pipeline documentation that 0002 relocates into the overlay.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
