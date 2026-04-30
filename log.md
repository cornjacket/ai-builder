# Work Log

A date-ordered record of work in this repository at **task / question /
concept** granularity — *not* per prompt. Multiple prompts inside the same
task share a single entry; a new entry is opened only when the focus changes
(a new task starts, the user asks a substantively different question, or a
meaningfully new concept comes up).

Each entry is one or two sentences of *what changed and why*. The diff and
`git log` carry the rest. Every entry ends with the short commit hash that
delivered the work, plus the fully-qualified task name (and subtask name,
when applicable) that drove it.

The enforcing rule lives in [`CLAUDE.md`](CLAUDE.md#work-log). Background
and rationale: [`ai-builder-lessons/lessons/038-work-log-at-task-granularity.md`](../../ai-builder-lessons/lessons/038-work-log-at-task-granularity.md).

## Entry format

```
- **YYYY-MM-DD** — <one or two sentences>. Task: `<hex-id>-<task-name>`. [Subtask: `<hex-id>-<NNNN>-<subtask-name>`.] Commit: `<short-hash>`.
```

Subtask is included only when the entry is subtask-scoped. Use the
fully-qualified name (matching the task README heading and the `Task:` /
`Subtask:` commit trailers).

## Hash back-fill

When an entry is written before its commit lands, the hash is left as
`_pending_` and back-filled directly into `log.md` after the commit using
`scripts/log-add.sh --backfill`. The back-fill leaves `log.md` dirty; the
change rides into the next task's commit. **Never create a dedicated commit
just to back-fill the hash** — two commits per task is a smell.

## Entries

- **2026-04-30** — Introduced `log.md`, the enforcing CLAUDE.md `## Work Log` rule, and `scripts/log-add.sh` for adding entries and back-filling commit hashes. Task: `14fb29-add-work-log-mechanism`. Commit: `_pending_`.
