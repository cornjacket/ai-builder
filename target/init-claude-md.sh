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

SECTION=$(cat <<'EOF'
<!-- task-management-start -->
## Task Management

All work in this repository is tracked through a structured task management
system. Before starting any work, check the task system to understand current
priorities and status.

**Full documentation:** [`project/tasks/README.md`](project/tasks/README.md)

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

> **Rule:** When a subtask is finished, always run `complete-task.sh --parent`
> to mark it `[x]` before moving on to the next subtask.

> **Rule:** Subtask `Status` is binary — only `—` (not done) or `complete`
> (done). Subtasks do not have statuses like `draft`, `backlog`, or
> `in-progress`; those apply only to top-level tasks.

### Scripts

Run from the repo root:

```bash
project/tasks/scripts/new-task.sh       --epic main --folder draft --name <task>
project/tasks/scripts/new-task.sh       --epic main --folder draft --parent <task> --name <subtask>
project/tasks/scripts/move-task.sh      --epic main --name <task> --from <status> --to <status>
project/tasks/scripts/complete-task.sh  --epic main --folder <status> --name <task>
project/tasks/scripts/complete-task.sh  --epic main --folder <status> --parent <task> --name <subtask>
project/tasks/scripts/show-task.sh      --epic main --folder <status> --name <task>
project/tasks/scripts/delete-task.sh    --epic main --folder <status> --name <task>
project/tasks/scripts/restore-task.sh   --epic main --folder <status> --name <task>
project/tasks/scripts/list-tasks.sh     --epic main [--folder <status>] [--depth <n>] [--all] [--tag <tag>]
```
<!-- task-management-end -->
EOF
)

# ---------------------------------------------------------------------------
# Create or append CLAUDE.md
# ---------------------------------------------------------------------------

if [[ ! -f "$CLAUDE_MD" ]]; then
    cat > "$CLAUDE_MD" <<EOF
# AI Agent Instructions

$SECTION
EOF
    echo "Created: CLAUDE.md"
else
    if grep -q "<!-- task-management-start -->" "$CLAUDE_MD"; then
        echo "Task management section already present in CLAUDE.md — skipping."
    else
        printf "\n%s\n" "$SECTION" >> "$CLAUDE_MD"
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
