# Task: add-work-log-mechanism

| Field       | Value                  |
|-------------|------------------------|
| Task-type   | USER-TASK              |
| Status | in-progress |
| Epic        | main               |
| Tags        | process,docs               |
| Priority    | HIGH           |
| Category    | task-tooling           |
| Created     | 2026-04-30            |
| Completed   | —                      |
| Next-subtask-id | 0004 |

## Goal

Introduce a repo-root `log.md` work-log mechanism — a date-ordered record of
work at task / question / concept granularity, indexed by short commit hash —
plus an enforcing rule in `CLAUDE.md` and a small helper script for adding
and back-filling entries.

## Context

Adopted from
[`ai-builder-lessons/lessons/038-work-log-at-task-granularity.md`](../../../../../ai-builder-lessons/lessons/038-work-log-at-task-granularity.md).
The lesson observes that `git log` is too granular to skim and that AI
sessions amplify the gap between "what changed" (the diff) and "what were we
working on" (the task). A `log.md` at the repo root, paired with an enforcing
rule, closes that gap by giving a short, date-ordered, hash-indexed record at
task granularity.

The lesson is explicit that the file and the rule must ship together — one
without the other is a half-measure. It also forbids dedicated back-fill
commits: when an entry is written before its commit lands, the hash is
back-filled directly into `log.md` and rides into the next task's commit.

**Design decisions for this implementation:**

- **Entry format** — `- **YYYY-MM-DD** — <description>. Task: \`<id>-<name>\`. [Subtask: \`<id>-<NNNN>-<name>\`.] Commit: \`<short-hash>\`.`
  Subtask is included only when the entry is subtask-scoped. The format mirrors
  the existing commit-trailer convention from the Git Commits section of CLAUDE.md.
- **CLAUDE.md placement** — new top-level `## Work Log` section between
  `## Git Commits` and `## Brainstorming`, with a one-line cross-reference
  from the Git Commits section (since hash discipline is shared).
- **Rule style** — match existing convention (`> **Rule:**` blocks, not
  numbered). Rule must call out both failure modes (entries-per-prompt and
  tasks-without-entries), require the hash, and forbid dedicated back-fill
  commits.
- **Scripts** — one helper at `scripts/log-add.sh` with two modes:
  default appends a new entry with a `_pending_` hash; `--backfill` replaces
  the most recent `_pending_` with `git rev-parse --short HEAD`. No combined
  "update + commit" script — that would impose structure on commit messages
  and conflict with the existing task-trailer convention. Scripts dir is new
  (top-level `scripts/`); `bootstrap/` is reserved for workspace-setup scripts.

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
- [x] [X-14fb29-0000-create-log-md](X-14fb29-0000-create-log-md/)
- [x] [X-14fb29-0001-add-claude-md-work-log-rule](X-14fb29-0001-add-claude-md-work-log-rule/)
- [x] [X-14fb29-0002-implement-log-add-script](X-14fb29-0002-implement-log-add-script/)
- [x] [X-14fb29-0003-update-documentation](X-14fb29-0003-update-documentation/)
<!-- subtask-list-end -->

## Notes

_None._
