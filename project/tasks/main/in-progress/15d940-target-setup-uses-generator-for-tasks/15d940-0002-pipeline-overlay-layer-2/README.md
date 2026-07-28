# Task: pipeline-overlay-layer-2

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

Settle what the layer-2 pipeline overlay actually installs into a target, and
remove what layer 1 now supersedes.

## Context

**Decision: the overlay is thin — the 7 task-facing pipeline scripts only.**
The orchestrator, its state machines and its role prompts are *not* installed
into targets.

This deliberately departs from
`create-project-system/docs/composition-with-create-ai-builder.md`, which
describes layer 2 as "the 7 pipeline scripts + orchestrator/roles/machines"
installed on top. The code does not support the second half:

- `orchestrator.py:182` sets `PM_SCRIPTS_DIR = TARGET_REPO/project/tasks/scripts`,
  and the handlers shell out to it — `decompose.py` invokes the target's
  `new-pipeline-subtask.sh` and `set-current-job.sh`, `lch.py` invokes its
  `on-task-complete.sh`. So the 7 scripts genuinely must be in the target.
- Nothing reads `orchestrator/`, `machines/` or `roles/` from a target. The
  orchestrator runs from a create-ai-builder checkout, takes `--state-machine`
  as a path relative to *that* repo, and reaches into the target via
  `--target-repo`.

Installing the engine into every target would therefore be dead weight today,
and would recreate for layer 2 exactly the copy-of-a-copy drift that moving
layer 1 to a pinned generator exists to eliminate. If a target ever needs to
run builds without a create-ai-builder checkout, that is a real feature with
its own design — not a side effect of setup copying a directory.

**Deleted `target/`'s hand-maintained `project/` template.** Its
`tasks/README.md` is fully superseded by the generated `project/tasks/docs/`:
the generator's `README.md` already documents the three task types including
PIPELINE-SUBTASK, the hierarchy rules, the task-format headers and the
pipeline commands. Nothing was worth relocating, so no layer-2 doc file was
created. Verified no live code referenced the template (the one
`target/project/...` hit in `tests/regression/lib/replay-lib.sh` is a path
inside a recording snapshot whose target repo is coincidentally named
`target/`).

## Notes

Two hand-offs for the upstream create-project-system repo, neither actionable
from here:

1. `docs/composition-with-create-ai-builder.md` should be corrected — layer 2
   is the 7 scripts, not "+ orchestrator/roles/machines".
2. The generated `project/tasks/docs/README.md` documents pipeline commands
   (`new-pipeline-build.sh`, `set-current-job.sh`) that `generate.sh` does not
   install. Harmless here because create-ai-builder overlays them, but for a
   plain create-project-system consumer those docs describe missing scripts.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
