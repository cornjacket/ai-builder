# Task: regression-targets-must-be-git-repos

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | in-progress |
| Epic        | main               |
| Tags        | —               |
| Priority    | HIGH           |
| Category    | regression-infra           |
| Created     | 2026-08-03            |
| Completed   | —                      |
| Next-subtask-id | 0004 |

## Goal

Make every regression target its own git repo, and make a non-git target fail
loudly at install time, so a target's task scripts can never operate on
create-ai-builder itself.

## Context

**The bug.** The generated task scripts resolve the repo root by asking git,
from the scripts' own directory (`task-env.sh` → `resolve_repo_root()`, which
tries `git rev-parse --show-toplevel` first and only walks up for a `.git` or
`TASKS_REL` marker if git fails). Every regression harness creates its target
with `rm -rf` + `mkdir -p` and nothing else, so the target is a plain directory
**inside** the create-ai-builder repo. git therefore answers with the enclosing
repo, and the target's scripts read and write create-ai-builder's own
`project/tasks/`.

**Observed, not theorised:** running `list-tasks.sh` from inside
`sandbox/regressions/template-setup/target` printed this repo's real backlog
(`4f9fba-add-model-selection-to-machine-config`, `d99044-per-role-model-tiering`,
…). `new-epic.sh` aborted with "Epic already exists: project/tasks/main" because
it was inspecting create-ai-builder's epic, not the target's.

**Severity.** `list-tasks.sh` is read-only, but `new-user-task.sh`,
`move-task.sh` and `complete-task.sh` are not. A pipeline regression run against
a non-git target can create and move tasks in this repo's real task tree. Do not
run the pipeline regressions until this lands.

**Origin.** Pre-existing since PR #4, which made this repo's task scripts
generated and git-aware; `setup-project.sh` then copied those same scripts into
targets. Not introduced by `15d940-target-setup-uses-generator-for-tasks` —
that task merely surfaced it, because setup now calls `new-epic.sh`, which
fails loudly instead of silently misresolving.

**Fix, both halves together so nothing breaks in between:**

1. `git init` the target in every regression harness that creates one —
   unconditionally, whether or not that test appears to use the task system.
   We cannot know in advance which scripts a harness will reach for, and the
   failure mode is silent, so the safe assumption is always.
2. A guard in `target/setup-project.sh` that refuses to install into a
   directory which is not its own git repo root, with a message naming the
   cause. Without this, the next harness written without `git init` reproduces
   the bug silently.

Both halves belong in one change: the guard alone would break every existing
pipeline harness, and the `git init`s alone would leave the trap armed for the
next author.

**Harnesses to fix** (none currently run `git init`):

- `tests/regression/user-service/reset.sh`
- `tests/regression/platform-monolith/reset.sh`
- `tests/regression/doc-user-service/reset.sh`
- `tests/regression/doc-platform-monolith/reset.sh`
- `tests/regression/user-service/component-tests/run.sh`

`tests/regression/template-setup/test.sh` is being fixed inside
`15d940-target-setup-uses-generator-for-tasks`, which already owns that file —
see the sequencing note below.

## Notes

**Sequencing with 15d940.** 15d940 sits at 6/8 subtasks on branch
`workspace-mgmt`. Its subtask 0006 cannot pass until its own target is
git-init'd, so the one-line fix for `template-setup/test.sh` stays in 15d940.
The guard in `setup-project.sh` belongs **here**, not there, so that it lands
in the same change as the five harness fixes it would otherwise break.

**Open question for whoever picks this up:** whether the five pipeline
regressions have been run since PR #4 merged. If they have, this repo's task
tree may already contain writes made by those runs, and it is worth auditing
`git log` over `project/tasks/` for task moves nobody made deliberately.

**Worth considering upstream:** whether `resolve_repo_root()` preferring git
over the `TASKS_REL` marker is the right precedence. The non-git fallback would
have found the target correctly; git wins first and gets it wrong. Changing
that is a create-project-system decision, not one to make here.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [ ] [abe6a1-0000-add-git-init-to-pipeline-harnesses](abe6a1-0000-add-git-init-to-pipeline-harnesses/)
- [ ] [abe6a1-0001-guard-non-git-target-in-setup](abe6a1-0001-guard-non-git-target-in-setup/)
- [ ] [abe6a1-0002-verify-target-isolation](abe6a1-0002-verify-target-isolation/)
- [ ] [abe6a1-0003-document-the-requirement](abe6a1-0003-document-the-requirement/)
<!-- subtask-list-end -->

## Notes

_None._
