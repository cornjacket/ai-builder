# `log-add.sh`

Add an entry to the repo-root [`log.md`](../../log.md), or back-fill the most
recent `_pending_` hash with the current short HEAD. Does not commit.

## Usage

**Append a new entry:**

```bash
project/scripts/log-add.sh --task <task-name> [--subtask <subtask-name>] [--epic <epic>] -- <description>
```

The description is everything after `--`. The script prepends today's date,
formats the entry per the [Work Log](../../CLAUDE.md#work-log) convention,
and appends it to `log.md` with `_pending_` as the hash placeholder.

**Back-fill the most recent `_pending_`:**

```bash
project/scripts/log-add.sh --backfill
```

Replaces the last `_pending_` in `log.md` with `git rev-parse --short HEAD`.
Leaves `log.md` dirty — the change rides into the next task's commit.

## Workflow

1. Append the entry **before** committing the work it describes:
   ```bash
   project/scripts/log-add.sh --task 14fb29-add-work-log-mechanism -- "Did the thing."
   ```
2. Stage `log.md` alongside your other changes and commit normally (with
   the standard task trailers).
3. After the commit lands, back-fill the hash:
   ```bash
   project/scripts/log-add.sh --backfill
   ```
4. The dirty `log.md` rides into the next task's commit.

**Never create a dedicated commit just to back-fill a hash** — see lesson 038
([`ai-builder-lessons/lessons/038-work-log-at-task-granularity.md`](../../../../ai-builder-lessons/lessons/038-work-log-at-task-granularity.md))
for the rationale.

## Validation

- `--task <name>` must resolve to a directory under
  `project/tasks/<epic>/{draft,backlog,in-progress,complete,wont-do}/`.
- `--subtask <name>` (when given) must resolve to either `<name>` or
  `X-<name>` under the parent task directory (`X-` prefix marks completed
  subtasks).
- `--backfill` errors if no `_pending_` is present in `log.md`.
- `log.md` must exist; the script will not create it.

## Why no combined "update + commit" mode

Commits in this repo carry task trailers and varying message bodies. Wrapping
the commit step would either impose a rigid format (conflicting with the
existing convention in [`CLAUDE.md` § Git Commits](../../CLAUDE.md#git-commits))
or duplicate work the agent already does. Staging `log.md` alongside the
working changes and committing normally is the simplest and most flexible
flow.
