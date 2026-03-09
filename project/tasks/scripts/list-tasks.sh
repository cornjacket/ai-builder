#!/usr/bin/env bash
# List all tasks in an epic, grouped by status.
# Optionally filter to a single status folder.
#
# Usage:
#   list-tasks.sh [--epic <epic>] [--folder <status>]
#
# Example:
#   list-tasks.sh --epic main
#   list-tasks.sh --epic main --folder backlog

set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPTS_DIR/../../.." && pwd)"

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------

EPIC="main"
FOLDER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --epic)   EPIC="$2";   shift 2 ;;
        --folder) FOLDER="$2"; shift 2 ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
done

EPIC_DIR="$REPO_ROOT/project/tasks/$EPIC"

if [[ ! -d "$EPIC_DIR" ]]; then
    echo "Epic not found: $EPIC"
    exit 1
fi

# Status display order
STATUSES=("inbox" "draft" "backlog" "in-progress" "complete" "wont-do")

# ---------------------------------------------------------------------------
# Print task tree
# ---------------------------------------------------------------------------

print_tasks() {
    local status_dir="$1"
    local status="$2"
    local has_tasks=0

    # Find direct task directories (depth 1 under status dir)
    while IFS= read -r task_dir; do
        if [[ ! -f "$task_dir/README.md" ]]; then continue; fi
        task_name="$(basename "$task_dir")"

        if [[ $has_tasks -eq 0 ]]; then
            echo ""
            echo "  [$status]"
            has_tasks=1
        fi

        echo "    $task_name"

        # Find subtasks (depth 1 under task dir)
        while IFS= read -r subtask_dir; do
            if [[ ! -f "$subtask_dir/README.md" ]]; then continue; fi
            subtask_name="$(basename "$subtask_dir")"
            echo "      └── $subtask_name"
        done < <(find "$task_dir" -mindepth 1 -maxdepth 1 -type d | sort)

    done < <(find "$status_dir" -mindepth 1 -maxdepth 1 -type d | sort)
}

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

echo "Tasks — epic: $EPIC"
echo "========================================"

if [[ -n "$FOLDER" ]]; then
    status_dir="$EPIC_DIR/$FOLDER"
    if [[ ! -d "$status_dir" ]]; then
        echo "Status folder not found: $FOLDER"
        exit 1
    fi
    print_tasks "$status_dir" "$FOLDER"
else
    for status in "${STATUSES[@]}"; do
        status_dir="$EPIC_DIR/$status"
        if [[ -d "$status_dir" ]]; then
            print_tasks "$status_dir" "$status"
        fi
    done
fi

echo ""
