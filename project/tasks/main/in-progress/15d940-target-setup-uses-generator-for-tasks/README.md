# Task: target-setup-uses-generator-for-tasks

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | in-progress |
| Epic        | main               |
| Tags        | —               |
| Priority    | MED           |
| Category    | workspace-mgmt           |
| Created     | 2026-07-26            |
| Completed   | —                      |
| Next-subtask-id | 0008 |

## Goal

Refactor `target/setup-project.sh` so a target repo's **task layer** comes from a
**pinned** create-project-system `generate.sh` (one hop, single source), while
create-ai-builder installs its **pipeline** as an overlay on top. Removes the
current copy-of-a-copy.

## Context

Re-homed from create-project-system (its placeholder task 14). Design doc:
`create-project-system/docs/composition-with-create-ai-builder.md`.

`target/setup-project.sh` currently installs the target's task system by copying
this repo's **own** `project/tasks/scripts/`. After the migration those scripts
are themselves generated, so it's a **copy-of-a-copy** with two drift points, and
the script hand-re-implements epic scaffolding + CLAUDE.md init that `generate.sh`
already does better.

Two layers, two owners:
- **Layer 1 (task system)** → delegate to a **pinned** `generate.sh`
  (`--with-status --with-skill --inject-claude-md` …). That single call lands the
  scripts, `USING.md`, the `task-system` **skill**, and the CLAUDE.md block.
- **Layer 2 (pipeline)** → create-ai-builder's own overlay — the 7 pipeline
  scripts + orchestrator/roles/machines. **Not** from `generate.sh`.

**Pinned version decided** (submodule at a pinned commit vs vendored snapshot —
pick during execution). Coordinate with `29297c-relocate-pipeline-scripts` (the
overlay should source the relocated pipeline dir, not the generated mount).

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-15d940-0000-vendor-pinned-create-project-system](X-15d940-0000-vendor-pinned-create-project-system/)
- [x] [X-15d940-0001-delegate-layer-1-to-generate](X-15d940-0001-delegate-layer-1-to-generate/)
- [x] [X-15d940-0002-pipeline-overlay-layer-2](X-15d940-0002-pipeline-overlay-layer-2/)
- [x] [X-15d940-0003-retire-init-claude-md](X-15d940-0003-retire-init-claude-md/)
- [ ] [15d940-0004-define-reinstall-contract](15d940-0004-define-reinstall-contract/)
- [ ] [15d940-0005-update-verify-setup](15d940-0005-update-verify-setup/)
- [ ] [15d940-0006-sandbox-install-regression](15d940-0006-sandbox-install-regression/)
- [ ] [15d940-0007-update-affected-documentation](15d940-0007-update-affected-documentation/)
<!-- subtask-list-end -->

## Notes

_None._
