# AI Agent Instructions — ai-builder

## Development Workflow (Git Worktrees)

This repository uses a git worktree workspace. The layout on disk is:

```
ai-builder/          ← workspace root (not a working tree itself)
    .bare/           ← bare clone (git object store)
    .git             ← pointer file to .bare/
    main/            ← worktree for 'main' branch  ← you are here
    <branch>/        ← ephemeral worktrees for feature branches
```

**All workflow scripts must be run from the `main/` worktree.** Each script
enforces this with a guard and fetches remote state before acting.

**Starting work on a task (move to in-progress + create worktree):**
```bash
bash bootstrap/new-workflow.sh -taskname <hex-id>-<task-name> -name <worktree-name>
# Moves task to in-progress, commits, creates ai-builder/<worktree-name>/
```

**Removing a worktree after merging (atomic — verifies merged PR via gh first):**
```bash
bash bootstrap/remove-worktree.sh <worktree-name>
```

Each worktree has its own `sandbox/` — regression runs in different worktrees
do not interfere with each other.

**`ai-builder-gold/`** is the archived pre-migration repo. It is read-only
and should not be modified.

---

## Tool Usage

Prefer dedicated tools over Bash for file operations — they never require
permission prompts:

- **Read files** → `Read` tool (not `cat`, `head`, `tail`)
- **Search content** → `Grep` tool (not `grep`, `rg`)
- **Find files** → `Glob` tool (not `find`, `ls`)

Reserve `Bash` for operations with no dedicated tool equivalent: running
tests, git commands, script execution, and similar shell tasks.

---

## Workflow Guideline

All work in this repository — whether human or AI driven — must be tracked
through the task management system before implementation begins. This applies
to features, fixes, refactors, and documentation. Work in `/sandbox` is
exempt; the sandbox is for unstructured experimentation.

**Before starting any work outside `/sandbox`:**
1. Check whether a task already exists for the work.
2. If not, create one using `new-user-task.sh` and move it to `in-progress/`.
3. Do the work.
4. Move the task to `complete/` when done.

**`/sandbox` usage:** the sandbox is for unstructured experimentation and
regression test artefacts. Regression tests that need a live task system
(target repos, output dirs) must create them under `sandbox/` — never under
`/tmp` or other locations outside the repo.

**After completing a task or subtask:** concisely explain what was just done
and why in one short sentence, then suggest the next steps.

---

## Session Status

`project/status/` contains daily session logs (`YYYY-MM-DD.md`). **At the
start of every session, read the most recent status file** to understand where
things left off — what was in progress, what decisions were made, what is
coming up next.

**Sign-off:** when the user says "sign off", write a status summary to
`project/status/YYYY-MM-DD.md` covering: work completed, work in progress,
next up, and any key decisions. Also add a new row to the top of the log
table in `project/status/README.md` with the date and a one-line summary.
This is how context survives across sessions.

**Reviews:** `project/reviews/` contains session review documents named
`YYYY-MM-DD.md`. Reviews examine workflow, collaboration patterns, and AI
behaviour — not just code. When the user asks for a review, create a new
review doc using today's date. Reviews should be done at least once per major
task or milestone. Each critique should include the user's response and a
revised position where applicable.

**Full documentation:** [`project/README.md`](project/README.md)

---

## Pipeline Agent Knowledge Boundary

This `CLAUDE.md` is for **human and Oracle operators**. It is **not** injected
into pipeline agent prompts (agents run with `cwd=output_dir`, not the repo
root, so CLAUDE.md is not loaded by the agent CLI).

Pipeline AI agents (ARCHITECT, IMPLEMENTOR, TESTER) know only:
- The job document (`README.md`) — provided by path in the prompt
- Target-repo build/test commands — from `## Suggested Tools` in the job doc

They have zero knowledge of:
- Task management scripts (`new-pipeline-subtask.sh`, `complete-task.sh`, etc.)
- `task.json` — its structure or location
- `last-job.json` — how the pipeline advances (written after each stage)
- Any orchestrator internals

This boundary is enforced by keeping script/orchestrator knowledge out of all
`roles/*.md` files. See [`ai-builder/orchestrator/README.md`](ai-builder/orchestrator/README.md)
for the formal boundary definition.

---

## Regression Tests

**Never start a regression run without explicit user approval.** Do not reset,
launch the orchestrator, or start any pipeline run unless the user has directly
asked you to run the regression in the current message. Completing a task or
committing code does not imply permission to run a regression.

**Never start a regression run if one is already in progress.** Before running
`reset.sh` or launching the orchestrator, check whether a pipeline is currently
running by inspecting the Level: TOP pipeline-subtask README in the target repo.
`reset.sh` enforces this automatically — it will abort if the current pipeline
is incomplete. Do not use `--force` unless you have confirmed the pipeline
process is no longer running.

Only one regression run may be active per worktree at a time. Each worktree has
its own `sandbox/regressions/` directory, so runs in different worktrees are
independent. Within a single worktree, two concurrent runs will corrupt each
other's task trees and token data.

---

## Task Management

All work in this repository is tracked through a structured task management
system. Before starting any work, check the task system to understand current
priorities and status.

**Full documentation:** [`project/tasks/README.md`](project/tasks/README.md)

### Task Types

There are three task types. Every task README has a `Task-type` field
identifying which type it is.

**USER-TASK** — top-level, human/Oracle-owned. All top-level work must be a
user-task. No Parent field, no pipeline sections. Created with `new-user-task.sh`.

**USER-SUBTASK** — human/Oracle-owned subtask. Used for planning steps,
reviews, approvals, research. Does not go to the pipeline. Can contain further
user-subtasks or pipeline-subtasks. Created with `new-user-subtask.sh`.

**PIPELINE-SUBTASK** — the pipeline's unit of work. A `build-N` entry point
authored by the Oracle and submitted to the orchestrator, or a pipeline-internal
node (component, integrate, test) created by the TM. Pipeline-owned once
submitted. Can only contain pipeline-subtasks. Entry points are created with
`new-pipeline-build.sh`; internal nodes are created by the pipeline itself via
`new-pipeline-subtask.sh`.

**Hierarchy rules:**
- All top-level work must be a user-task
- user-task → user-subtasks and/or pipeline-subtasks
- user-subtask → user-subtasks and/or pipeline-subtasks
- pipeline-subtask → pipeline-subtasks only
- No human-owned node may appear under a pipeline-owned node

### Summary

Tasks are organized by epic and status. Each task is a directory containing a
`README.md` that describes the work. Subtasks are subdirectories of their
parent task.

**Naming convention:**
- Top-level tasks: `{6-char-hex-id}-{name}` (e.g. `a3f2c1-my-task`)
- Subtasks: `{parent-short-id}-{NNNN}-{name}` (e.g. `a3f2c1-0001-design-review`)

The `NNNN` four-digit number **defines the implementation order** of subtasks within
a parent task. Subtasks must be worked in ascending `NNNN` order unless explicitly
noted otherwise. The number is assigned at creation time by `Next-subtask-id` in
the parent's metadata and incremented automatically by the creation scripts.

If the intended implementation order changes after creation, use
`project/tasks/scripts/reorder-subtasks.py` to renumber the directories to match
the new order. Never implement subtasks out of their numbered sequence without
first reordering them — the numbers are the contract.

When a subtask is completed, its directory is renamed with an `X-` prefix
(e.g. `X-a3f2c1-0001-design-review`). The `X-` prefix marks the subtask as done
and preserves its number for audit purposes. Completed subtasks are shown with
`[x]` in the parent README's subtask list.

```
project/tasks/
    <epic>/
        inbox/        # raw ideas, not yet evaluated
        draft/        # being written up
        backlog/      # refined, ordered by priority — pull from here
        in-progress/  # actively being worked on
        complete/     # done and verified
        wont-do/      # explicitly decided against
```

**When picking up work:** pull from `backlog/` in top-to-bottom order.
**When starting a task:** move it to `in-progress/` using `move-task.sh`.
**When done:** run `complete-task.sh` — no `--parent` for top-level tasks, add `--parent` for subtasks.

**To show outstanding work** (draft + backlog + in-progress, excluding complete):
```bash
project/tasks/scripts/list-tasks.sh --epic main --folder draft --depth 2
project/tasks/scripts/list-tasks.sh --epic main --folder backlog --depth 2
project/tasks/scripts/list-tasks.sh --epic main --folder in-progress --depth 2
```
Add `--sort-priority` to any of the above to order tasks HIGH → MED → LOW → unset:
```bash
project/tasks/scripts/list-tasks.sh --epic main --folder backlog --sort-priority
project/tasks/scripts/list-tasks.sh --epic main --folder draft --sort-priority
project/tasks/scripts/list-tasks.sh --epic main --folder in-progress --sort-priority
```
Do NOT use `list-tasks.sh --epic main` without `--folder` when the user asks for
outstanding or incomplete tasks — it includes `complete/` which adds noise.

> **Rule:** Before beginning any task or subtask, describe its purpose and
> list all subtasks in order. If the task manager is human, wait for their
> approval before starting any implementation work.

> **Rule:** Always use the scripts to manage tasks. Never manually edit task
> `README.md` files to add or remove subtasks, and never manually move task
> directories between status folders. The scripts keep the filesystem and
> documentation in sync.

> **Rule:** Never create task directories or write task README files directly
> using shell commands (`cat`, `mkdir`, heredocs, etc.). Always use the
> provided scripts (`new-user-task.sh`, `new-user-subtask.sh`,
> `new-pipeline-subtask.sh`). Use `Edit` or `Write` only to fill in content
> sections (Goal, Context, Notes) after a script has created the file.

> **Rule:** When a subtask is finished, always run `complete-task.sh --parent`
> to mark it `[x]` before moving on to the next subtask.

> **Rule:** Subtask `Status` is binary — only `—` (not done) or `complete`
> (done). Subtasks do not have statuses like `draft`, `backlog`, or
> `in-progress`; those apply only to top-level tasks.

> **Rule:** When testing a new feature, leave the test task in place after
> verification. Move it to `complete/` using `move-task.sh` rather than
> deleting it. Test tasks serve as living examples of correct usage.

> **Rule:** Every new task must include a final subtask to create or update
> documentation. Add it as the last NNNN-numbered subtask before beginning any
> implementation work. A task is not closeable without it.

> **Rule:** Always ask the user before closing (moving to `complete/`) a task
> or subtask. Do not close tasks unilaterally as part of other work. Wait for
> explicit confirmation before running `complete-task.sh` or
> `move-task.sh --to complete`.

> **Rule:** Always refer to tasks by their fully-qualified name:
> `{hex-id}-{task-name}` for top-level tasks (e.g. `4603fa-pipeline-record-replay`),
> and `{hex-id}-{NNNN}-{subtask-name}` for subtasks (e.g. `4603fa-0012-document-how-to-add-replay-regression`).
> Never refer to a task by hex ID alone (e.g. `4603fa`) — the name is required
> for anyone reading the conversation to know what is being discussed.

> **Rule:** Every new USER-TASK must have its `Category:` field set immediately
> after creation. Assign it the branch name of the matching worktree class from
> [`project/tasks/classes.md`](project/tasks/classes.md). If no class fits, set
> it to `unclassified`. Never leave `Category:` as `—` on a USER-TASK.

### Task granularity

A top-level task should be completable in a single ARCHITECT → IMPLEMENTOR → TESTER
pipeline run. **Split a task when** IMPLEMENTOR would touch more than ~5 unrelated
files or implement more than ~3 independent concerns. A subtask should be a single,
verifiable action (e.g. "write function X", "add migration Y") — not a phase or theme.
When in doubt, smaller is better.

**Break a task down further when:**
- ARCHITECT cannot produce a coherent design without first resolving an unknown
- IMPLEMENTOR would need to make a structural decision that warrants review
- Two parts are independently testable with no shared state

**Proceed as one task when:** all inputs/outputs are known, IMPLEMENTOR can work
linearly, TESTER can verify in one pass.

### TESTER failure decisions

| Failure type | Action |
|---|---|
| Bug in code just written | Create a new subtask in the current task for the fix; do not widen scope |
| Requirement misunderstood | Update the task description; restart the ARCHITECT for this task |
| Systemic issue (missing dependency, wrong environment) | Create a new blocking task; pause current task until resolved |
| Flaky test or environment noise | Retry the TESTER once; if it fails again, treat as a real failure |

### Scripts

Run from the repo root:

```bash
project/tasks/scripts/new-user-task.sh        --epic main --folder draft --name <task>
project/tasks/scripts/new-user-subtask.sh     --epic main --folder <status> --parent <task> --name <subtask>
project/tasks/scripts/new-pipeline-build.sh   --epic main --folder <status> --parent <task> [--name <name>]
project/tasks/scripts/new-pipeline-subtask.sh --epic main --folder <status> --parent <task> --name <subtask>
project/tasks/scripts/move-task.sh            --epic main --name <task> --from <status> --to <status>
project/tasks/scripts/complete-task.sh        --epic main --folder <status> --name <task>
project/tasks/scripts/complete-task.sh        --epic main --folder <status> --parent <task> --name <subtask>
project/tasks/scripts/show-task.sh            --epic main --folder <status> --name <task>
project/tasks/scripts/delete-task.sh          --epic main --folder <status> --name <task>
project/tasks/scripts/restore-task.sh         --epic main --folder <status> --name <task>
project/tasks/scripts/wont-do-subtask.sh      --epic main --folder <status> --parent <task> --name <subtask>
project/tasks/scripts/list-tasks.sh           --epic main [--folder <status>] [--depth <n>] [--root <path>] [--all] [--tag <tag>] [--sort-priority]
project/tasks/scripts/rename-subtask.sh       --epic main --folder <status> --parent <task> --name <subtask> --new-id NNNN
project/tasks/scripts/insert-subtask.sh       --epic main --folder <status> --parent <task> --at NNNN --name <name> [--type user|pipeline]
```

### Submitting a pipeline build run

The orchestrator (TM mode) requires the pipeline entry point to be a
**PIPELINE-SUBTASK with `Level: TOP`**. Never point the orchestrator at a
USER-TASK directly.

```bash
# 1. Create the build entry point under the user-task
README=$(project/tasks/scripts/new-pipeline-build.sh \
    --epic main --folder in-progress --parent <user-task-name> \
    | grep "^README:" | awk '{print $2}')

# 2. Fill in the Goal and Context in the created README, then run the orchestrator
python3 ai-builder/orchestrator/orchestrator.py \
    --job         "$README" \
    --target-repo <target-repo> \
    --output-dir  <output-dir> \
    --epic        main \
    --state-machine ai-builder/orchestrator/machines/builder/default.json
```

---

## Git Commits

Every commit must include task trailers so that commits can be traced back to
the task that motivated them. Add these as footer lines, after the body and
before `Co-Authored-By:`:

```
<subject line>

<optional body>

Task: {hex-id}-{task-name}
Subtask: {hex-id}-{NNNN}-{subtask-name}   ← include only when a specific subtask drove the commit

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

Use the fully-qualified task name (same convention as the task README heading).
Omit `Subtask:` for commits that span an entire task or are not tied to a
specific subtask. This makes `git log --grep="Task: {hex-id}"` an instant
audit trail for any task.

---

## Brainstorming

When the user says "let's brainstorm on X", "brainstorm X", or similar, immediately
create `sandbox/brainstorms/brainstorm-{subject}.md` before the discussion begins. Write design
decisions to that file in real time as the discussion unfolds — do not discuss first
and reconstruct afterward. The file is the record; chat is ephemeral.

---

## Documentation

When adding functionality to ai-builder (new flags, new roles, new pipeline
behaviour, new scripts), update or create documentation as part of the same
task:

- Every directory must have a `README.md`. If you create a new directory,
  create its README before moving on.
- Every `CLAUDE.md` must have a `GEMINI.md` symlink in the same directory.
  When creating a new `CLAUDE.md`, immediately run `ln -s CLAUDE.md GEMINI.md`
  in the same directory and include both in the same commit.
- Every source file should have a companion `.md` (e.g. `foo.py` → `foo.md`).
  Update the companion when the file's observable behaviour changes (inputs,
  outputs, side effects, design assumptions). Internal refactors that preserve
  the external contract do not require a doc update.
- Update the relevant `README.md` file index and overview when files are added,
  moved, or removed.

**Full documentation guideline:** [`ai-builder/docs/guidelines/documentation-standards.md`](ai-builder/docs/guidelines/documentation-standards.md)

