# Task: add-git-init-to-pipeline-harnesses

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-SUBTASK           |
| Status      | —                      |
| Epic        | main               |
| Tags        | —               |
| Parent      | abe6a1-regression-targets-must-be-git-repos             |
| Priority    | —           |
| Created     | 2026-08-03            |
| Completed   | —                      |
| Next-subtask-id | 0000               |

## Goal

Make every pipeline regression harness create its target as a real git repo, so
the target's task scripts resolve to the target and not to create-ai-builder.

## Context

Five harnesses built their target with `rm -rf` + `mkdir -p` and nothing else:

- `tests/regression/user-service/reset.sh`
- `tests/regression/platform-monolith/reset.sh`
- `tests/regression/doc-user-service/reset.sh`
- `tests/regression/doc-platform-monolith/reset.sh`
- `tests/regression/user-service/component-tests/run.sh`

Each now runs `git -C "$TARGET_REPO" init -q` straight after, with a comment
naming the failure mode — a bare `git init` reads as ceremony, and the next
author would delete it.

Applied unconditionally, not only to harnesses that visibly touch the task
system. Which scripts a harness ends up invoking is not knowable in advance,
and the failure is silent, so the safe assumption is always.

**Verified by containment, not by inspection.** Installed into a git-init'd
target nested inside this repo, then from inside it:

- `git rev-parse --show-toplevel` returns the *target*, not the worktree
- `list-tasks.sh` shows an empty backlog — the target's own — rather than
  create-ai-builder's 40-odd tasks, which is what it printed before the fix
- `new-user-task.sh` created `a21580-contained-write-probe` **inside the
  target**, with no corresponding directory appearing in this repo, and all
  three worktrees left with no unexpected tracked changes

The write probe is the one that matters: the original symptom was found with a
read, and a read cannot show whether writes are contained.

Note this subtask alone changes nothing for a harness someone writes next —
that is what `abe6a1-0001-guard-non-git-target-in-setup` is for, and why the
two land together.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
