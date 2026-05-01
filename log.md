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
`project/scripts/log-add.sh --backfill`. The back-fill leaves `log.md` dirty; the
change rides into the next task's commit. **Never create a dedicated commit
just to back-fill the hash** — two commits per task is a smell.

## Entries

- **2026-04-30** — Introduced `log.md`, the enforcing CLAUDE.md `## Work Log` rule, and `project/scripts/log-add.sh` for adding entries and back-filling commit hashes. Task: `14fb29-add-work-log-mechanism`. Commit: `69acb01`.
- **2026-04-30** — Relocated the work-log helper from top-level `scripts/` to `project/scripts/`, sibling of `project/tasks/scripts/`, keeping `bootstrap/` strictly about workspace setup. Task: `14fb29-add-work-log-mechanism`. Subtask: `14fb29-0004-relocate-scripts-to-project-scripts`. Commit: `7eb9115`.
- **2026-04-30** — Added `--category` flag to `new-user-task.sh`, validated against worktree branches in `classes.md` (plus `unclassified`); flag is required, the user-task template now substitutes `{{CATEGORY}}` instead of hardcoding `—`. Task: `4a8789-investigate-task-partitioning-for-parallel-worktrees`. Subtask: `4a8789-0000-add-category-flag-to-new-user-task`. Commit: `d442bd0`.
- **2026-04-30** — Fixed bats unit tests for new-user-task.sh that broke when --category became required (commit 9381b23 left main red); added regression tests for missing/invalid/unclassified category and symlinked classes.md into the test fixture. Task: `0b3c19-fix-new-user-task-bats-tests`. Commit: `fd5c9ce`.
- **2026-04-30** — Created backlog task to add a post-push CI checker that polls gh run and surfaces failures, after main was left red for ~1.5h and only caught by the user. Task: `6d4102-post-push-ci-check`. Commit: `da202a3`.
- **2026-04-30** — Ported the document-analyzer rule that Claude must announce log.md edits in chat with a literal '📝 log.md updated' line into ai-builder/CLAUDE.md's Work Log section, and folded the entry format, helper-script, and announcement directive into ai-builder-lessons lesson 038 so it stands alone as the reference. Task: `8312a3-port-log-md-update-emoji-rule`. Commit: `ee8ec8f`.
- **2026-04-30** — Closed the partition-analysis parent task: file-ownership map and 8 partition classes shipped to sandbox/task-partition-analysis.md and project/tasks/classes.md (both subtasks complete — --category flag in d442bd0 and the four ready-now worktrees acceptance-spec/docs/regression-infra/task-tooling created). Task: `4a8789-investigate-task-partitioning-for-parallel-worktrees`. Commit: `1ee92c4`.
- **2026-04-30** — Filed HIGH-priority task to resolve the overlap between log.md (per-task, hash-indexed, enforced) and project/status/YYYY-MM-DD.md (per-session sign-off, weaker enforcement); status's 'Work Completed' section restates log.md content while its unique value is intent and forward-looking state — design note pending in sandbox/. Task: `9d3bc1-resolve-log-md-vs-status-overlap`. Commit: `209005e`.
- **2026-05-01** — Resolved overlap between log.md and project/status/. Reframed status as a delta document covering the period since the previous report (operator-driven cadence, not daily); replaced the 'sign off' semantic with 'write a status report'. Updated CLAUDE.md, project/README.md, project/status/README.md, and the top-level README pointer. Task: `9d3bc1-resolve-log-md-vs-status-overlap`. Commit: `_pending_`.
