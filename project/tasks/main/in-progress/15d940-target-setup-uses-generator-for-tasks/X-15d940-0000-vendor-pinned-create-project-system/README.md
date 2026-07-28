# Task: vendor-pinned-create-project-system

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

Vendor the create-project-system generator into `vendor/create-project-system/`
at a pinned ref, so `target/setup-project.sh` has a reproducible layer-1 source
to delegate to. Record the pin such that drift is detectable.

## Context

Pin mechanism chosen: **vendored snapshot** (over git submodule or clone-on-
demand) — no network or submodule init at target-install time, works offline,
and a bump is a visible diff.

Pinned at `v0.1.0` = `c003956296d40db76f06fdda016e575486316580` (annotated tag,
cut upstream for this task; the repo had no tags before). The tag is the
readable handle, the SHA is what makes the install reproducible if the tag ever
moves — `PIN` records both.

Snapshot scope is `generate.sh` + `src/` only (41 files). `generate.sh`
resolves `src/` as a sibling of itself and reaches nothing else at runtime, so
the pair is self-contained; upstream's `tests/`, `tasks/`, `docs/` and planning
files are excluded.

Layer-1 contract at v0.1.0, verified against the vendored parser
(`generate.sh:53-62`): exactly ten flags — `--target-repo --tasks-dir --epic
--with-status --with-skill --inject-claude-md --with-classes --with-projects
--with-worktree-guard --force` — and no others. Generation is non-destructive
and re-runnable. **There is no `--with-pipeline`**: the generator never emits
pipeline machinery, so layer 2 stays a hand-owned create-ai-builder overlay.

The pin will need a bump by design — upstream task 19 renames `Category` →
`Worktree` and task 15 adds `--require-category`. Both are breaking here
(`Category:` is live in ~134 task metadata rows), so stay on v0.1.0 until
there is a tag with a stated migration position. Bump procedure is in
`vendor/README.md`.

Design doc stays upstream at
`create-project-system/docs/composition-with-create-ai-builder.md` — linked,
not copied.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
