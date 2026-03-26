#!/usr/bin/env bash
# Initialise CLAUDE.md in a target repository with a task management section,
# and create GEMINI.md as a symlink to CLAUDE.md.
#
# Usage:
#   init-claude-md.sh <target-repo-path>
#
# Example:
#   init-claude-md.sh ~/code/my-app

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------

TARGET_REPO=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -*) echo "Unknown flag: $1"; exit 1 ;;
        *)
            if [[ -z "$TARGET_REPO" ]]; then
                TARGET_REPO="$1"
            else
                echo "Unexpected argument: $1"
                exit 1
            fi
            shift
            ;;
    esac
done

if [[ -z "$TARGET_REPO" ]]; then
    echo "Usage: init-claude-md.sh <target-repo-path>"
    exit 1
fi

if [[ ! -d "$TARGET_REPO" ]]; then
    echo "Target repository not found: $TARGET_REPO"
    exit 1
fi

CLAUDE_MD="$TARGET_REPO/CLAUDE.md"
GEMINI_MD="$TARGET_REPO/GEMINI.md"

# ---------------------------------------------------------------------------
# Build the task management section
# ---------------------------------------------------------------------------

SECTION_FILE=$(mktemp)
trap 'rm -f "$SECTION_FILE"' EXIT

cat > "$SECTION_FILE" <<'HEREDOC'
## Brainstorming

When the user says "let's brainstorm on X", "brainstorm X", or similar, immediately
create `sandbox/brainstorm-{subject}.md` before the discussion begins. Write design
decisions to that file in real time as the discussion unfolds — do not discuss first
and reconstruct afterward. The file is the record; chat is ephemeral.

---

<!-- task-management-start -->
## Task Management

All work in this repository is tracked through a structured task management
system. Before starting any work, check the task system to understand current
priorities and status.

**Full documentation:** [`project/tasks/README.md`](project/tasks/README.md)

### Task Types

There are three task types. Every task README has a `Task-type` field.

**USER-TASK** — top-level, human/Oracle-owned. All top-level work must be a
user-task. No Parent field, no pipeline sections. Created with `new-user-task.sh`.

**USER-SUBTASK** — human/Oracle-owned subtask. Planning steps, reviews,
approvals, research. Does not go to the pipeline. Can contain further
user-subtasks or pipeline-subtasks. Created with `new-user-subtask.sh`.

**PIPELINE-SUBTASK** — the pipeline's unit of work. A `build-N` entry point
authored by the Oracle and submitted to the orchestrator, or a pipeline-internal
node (component, integrate, test) created by the TM. Pipeline-owned once
submitted. Can only contain pipeline-subtasks. Created with `new-pipeline-subtask.sh`.

**Hierarchy rules:**
- All top-level work must be a user-task
- user-task → user-subtasks and/or pipeline-subtasks
- user-subtask → user-subtasks and/or pipeline-subtasks
- pipeline-subtask → pipeline-subtasks only
- No human-owned node may appear under a pipeline-owned node

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

**Domain ownership:**
- **Frontend AI** (Oracle/human assistant): creates user-tasks, user-subtasks,
  and `build-N` pipeline-subtasks. Does NOT edit pipeline-internal subtasks
  once a build is submitted.
- **Orchestrator / TM**: operates on pipeline-subtasks and their internal
  children. Fills in Components, Design, AC. Creates component subtasks.
  Does NOT touch user-task or user-subtask READMEs.

### Workflow Rules

**Before beginning any task or subtask:** describe its purpose and list all
subtasks in order. If the task manager is human, wait for their approval
before starting any implementation work.

**When picking up work:** pull from `backlog/` in top-to-bottom order.
**When starting a task:** move it to `in-progress/` using `move-task.sh`.
**When done:** run `complete-task.sh` — no `--parent` for top-level tasks,
add `--parent` for subtasks.

> **Rule:** Always use the scripts to manage tasks. Never manually edit task
> `README.md` files to add or remove subtasks, and never manually move task
> directories between status folders.

> **Rule:** Never create task directories or write task README files directly
> using shell commands (`cat`, `mkdir`, heredocs, etc.). Always use the
> provided scripts. Use `Edit` or `Write` only to fill in content sections
> (Goal, Context, Notes) after a script has created the file.

> **Rule:** When a subtask is finished, always run `complete-task.sh --parent`
> to mark it `[x]` before moving on to the next subtask.

> **Rule:** Subtask `Status` is binary — only `—` (not done) or `complete`
> (done). Subtasks do not have statuses like `draft`, `backlog`, or
> `in-progress`; those apply only to top-level tasks.

### Scripts

Run from the repo root:

```bash
project/tasks/scripts/new-user-task.sh        --epic main --folder draft --name <task>
project/tasks/scripts/new-user-subtask.sh     --epic main --folder <status> --parent <task> --name <subtask>
project/tasks/scripts/new-pipeline-subtask.sh --epic main --folder <status> --parent <task> --name <subtask>
project/tasks/scripts/move-task.sh            --epic main --name <task> --from <status> --to <status>
project/tasks/scripts/complete-task.sh        --epic main --folder <status> --name <task>
project/tasks/scripts/complete-task.sh        --epic main --folder <status> --parent <task> --name <subtask>
project/tasks/scripts/show-task.sh            --epic main --folder <status> --name <task>
project/tasks/scripts/delete-task.sh          --epic main --folder <status> --name <task>
project/tasks/scripts/restore-task.sh         --epic main --folder <status> --name <task>
project/tasks/scripts/list-tasks.sh           --epic main [--folder <status>] [--depth <n>] [--all] [--tag <tag>]
```
<!-- task-management-end -->
HEREDOC

# ---------------------------------------------------------------------------
# Create or append CLAUDE.md
# ---------------------------------------------------------------------------

if [[ ! -f "$CLAUDE_MD" ]]; then
    { printf '# AI Agent Instructions\n\n'; cat "$SECTION_FILE"; printf '\n'; } > "$CLAUDE_MD"
    echo "Created: CLAUDE.md"
else
    if grep -q "<!-- task-management-start -->" "$CLAUDE_MD"; then
        echo "Task management section already present in CLAUDE.md — skipping."
    else
        { printf '\n'; cat "$SECTION_FILE"; printf '\n'; } >> "$CLAUDE_MD"
        echo "Updated: CLAUDE.md (task management section appended)"
    fi
fi

# ---------------------------------------------------------------------------
# Create GEMINI.md symlink
# ---------------------------------------------------------------------------

if [[ -e "$GEMINI_MD" || -L "$GEMINI_MD" ]]; then
    echo "GEMINI.md already exists — skipping."
else
    ln -s CLAUDE.md "$GEMINI_MD"
    echo "Created: GEMINI.md -> CLAUDE.md"
fi
