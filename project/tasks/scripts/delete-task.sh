#!/usr/bin/env bash
# Soft-delete a task or subtask.
#
# - Removes the entry from the parent directory's README.md.
# - Renames the task directory to .<name> (hidden, but not destroyed).
#
# Works for both top-level tasks and subtasks — the parent is always the
# containing directory, the same convention used by new-task.sh.
#
# Usage:
#   delete-task.sh --epic <epic> --folder <status> --name <task>
#   delete-task.sh --epic <epic> --folder <status> --parent <task> --name <subtask>
#
# Examples:
#   delete-task.sh --epic main --folder draft --name my-task
#   delete-task.sh --epic main --folder in-progress --parent my-task --name my-subtask

set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPTS_DIR/../../.." && pwd)"

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------

EPIC="main"
FOLDER=""
PARENT=""
NAME=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --epic)   EPIC="$2";   shift 2 ;;
        --folder) FOLDER="$2"; shift 2 ;;
        --parent) PARENT="$2"; shift 2 ;;
        --name)   NAME="$2";   shift 2 ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
done

if [[ -z "$FOLDER" || -z "$NAME" ]]; then
    echo "Usage: delete-task.sh --folder <status> --name <task> [--epic <epic>] [--parent <parent-task>]"
    exit 1
fi

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------

STATUS_DIR="$REPO_ROOT/project/tasks/$EPIC/$FOLDER"

if [[ -n "$PARENT" ]]; then
    PARENT_DIR="$STATUS_DIR/$PARENT"
else
    PARENT_DIR="$STATUS_DIR"
fi

TASK_DIR="$PARENT_DIR/$NAME"
HIDDEN_DIR="$PARENT_DIR/.$NAME"
PARENT_README="$PARENT_DIR/README.md"

if [[ ! -d "$TASK_DIR" ]]; then
    echo "Task not found: $TASK_DIR"
    exit 1
fi

if [[ ! -f "$PARENT_README" ]]; then
    echo "Parent README not found: $PARENT_README"
    exit 1
fi

if [[ -d "$HIDDEN_DIR" ]]; then
    echo "Hidden directory already exists: $HIDDEN_DIR"
    exit 1
fi

# ---------------------------------------------------------------------------
# Remove entry from parent README
# ---------------------------------------------------------------------------

# Matches both checked and unchecked subtask entries:  - [ ] [name](name/)  or  - [x] [name](name/)
# Also matches plain task-list entries:                - [name](name/)
if grep -q "\[$NAME\]($NAME/)" "$PARENT_README"; then
    sed -i '' "/\[$NAME\]($NAME\/)/d" "$PARENT_README"
else
    echo "Warning: no entry for '$NAME' found in $PARENT_README — skipping README update."
fi

# ---------------------------------------------------------------------------
# Rename directory to hidden
# ---------------------------------------------------------------------------

mv "$TASK_DIR" "$HIDDEN_DIR"

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

if [[ -n "$PARENT" ]]; then
    echo "Deleted subtask: project/tasks/$EPIC/$FOLDER/$PARENT/$NAME/ → .$NAME/"
else
    echo "Deleted task:    project/tasks/$EPIC/$FOLDER/$NAME/ → .$NAME/"
fi
echo "Updated:         $PARENT_README"
