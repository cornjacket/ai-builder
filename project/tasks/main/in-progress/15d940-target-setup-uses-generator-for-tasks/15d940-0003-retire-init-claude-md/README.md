# Task: retire-init-claude-md

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

Retire `target/init-claude-md.sh` now that the pinned generator injects the
CLAUDE.md block, and move the one thing it did that the generator does not —
the `GEMINI.md` symlink — into `setup-project.sh`.

## Context

**Not a clean deletion.** The generator writes the CLAUDE.md task-tracking
block (replace-in-place between `<!-- task-system:begin/end -->`, so it is
refreshable and never duplicated) but deliberately never creates `GEMINI.md`:
it is agent-neutral and does not assume any agent's filename. Its own
`src/skill/README.md` says as much — "if a repo symlinks `GEMINI.md →
CLAUDE.md`, parity is automatic". The symlink is a create-ai-builder
convention, so `setup-project.sh` now creates it under a "Repo conventions"
step. Without this, every target would have lost `GEMINI.md`, and
`verify-setup.sh` asserts it.

**Blast radius was larger than the file.** Call sites updated:

- `ai-builder/orchestrator/orchestrator.py` — held `INIT_SCRIPT` *and*
  `SETUP_SCRIPT` constants. Both were assigned and never read anywhere in the
  codebase; removed the dead pair rather than just the one.
- 5 regression scripts that ran it as a second install step:
  `user-service/reset.sh`, `platform-monolith/reset.sh`,
  `doc-user-service/reset.sh`, `doc-platform-monolith/reset.sh`,
  `user-service/component-tests/run.sh`.
- `tests/regression/template-setup/test.sh` — sections 3 and 4 tested the
  script directly. Rewritten to assert the *outcome* instead: setup produces
  `CLAUDE.md` containing the block, `GEMINI.md` as a symlink resolving to
  `CLAUDE.md`, and exactly one copy of the block. Note the sentinel changed
  from `task-management-start` to `task-system:begin`.
- Docs: root `README.md` TM-mode quick start, `target/SETUP.md` install steps,
  `how-to-write-a-regression-test.md` step 3, a stale comment in
  `component-tests/capture.sh`.

All touched shell scripts pass `bash -n`; `orchestrator.py` compiles.

**Not run here:** `template-setup/test.sh` is a regression test and needs
explicit approval. It will also still fail at section 5 until
`15d940-0005-update-verify-setup` lands — `verify-setup.sh` is stale
independently of this branch (it greps the old `task-management-start`
sentinel and checks a `task-template.md` that no longer exists).

## Notes

Six *other* task READMEs still describe `init-claude-md.sh` as a live file and
are now stale as plans — deliberately not edited here, since rewriting other
tasks' content is outside this subtask:

- backlog: `1aba9b-enforce-no-regression-without-permission`,
  `223838-audit-gemini-md-coverage`,
  `59d31e-add-completion-summary-to-target-claude-md`
- draft: `3230ef-design-workspace-claude-md-boundary`,
  `c526bd-add-status-and-reviews-to-target`,
  `37a660-design-oracle-and-pipeline-phases`

Each assumes a hand-written CLAUDE.md template that is now generated upstream;
they need re-pointing at the generator's snippet before they are worked.
Completed/wont-do tasks, status reports and reviews also mention it — those are
historical records and were left alone.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
