#!/usr/bin/env bash
# Create a new task directory with a template README.md.
# Appends the task to the status directory's README.md (creating it if needed).
#
# Usage:
#   new-task.sh --epic <epic> --folder <status> --name <task-name> [--tags <tags>]
#
# Example:
#   new-task.sh --epic main --folder draft --name create-project-management-system

set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPTS_DIR/../../.." && pwd)"

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------

EPIC="main"
FOLDER=""
NAME=""
TAGS="—"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --epic)   EPIC="$2";   shift 2 ;;
        --folder) FOLDER="$2"; shift 2 ;;
        --name)   NAME="$2";   shift 2 ;;
        --tags)   TAGS="$2";   shift 2 ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
done

if [[ -z "$FOLDER" || -z "$NAME" ]]; then
    echo "Usage: new-task.sh --folder <status> --name <task-name> [--epic <epic>] [--tags <tags>]"
    exit 1
fi

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

TASK_DIR="$REPO_ROOT/project/tasks/$EPIC/$FOLDER/$NAME"
STATUS_DIR="$REPO_ROOT/project/tasks/$EPIC/$FOLDER"
STATUS_README="$STATUS_DIR/README.md"

if [[ -d "$TASK_DIR" ]]; then
    echo "Task already exists: project/tasks/$EPIC/$FOLDER/$NAME"
    exit 1
fi

# ---------------------------------------------------------------------------
# Create task directory and README
# ---------------------------------------------------------------------------

mkdir -p "$TASK_DIR"

cat > "$TASK_DIR/README.md" << EOF
# Task: $NAME

| Field  | Value    |
|--------|----------|
| Status | $FOLDER  |
| Epic   | $EPIC    |
| Tags   | $TAGS    |
| Parent | —        |

## Description

_To be written._

## Subtasks

_None._

## Notes

_None._
EOF

# ---------------------------------------------------------------------------
# Create status README if it doesn't exist
# ---------------------------------------------------------------------------

if [[ ! -f "$STATUS_README" ]]; then
    cat > "$STATUS_README" << EOF
# $EPIC / $FOLDER

## Tasks

<!-- task-list-start -->
<!-- task-list-end -->
EOF
fi

# ---------------------------------------------------------------------------
# Append task to status README (before the end marker)
# ---------------------------------------------------------------------------

sed -i '' "s|<!-- task-list-end -->|- [$NAME]($NAME/)\n<!-- task-list-end -->|" "$STATUS_README"

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

echo "Created: project/tasks/$EPIC/$FOLDER/$NAME/"
echo "         project/tasks/$EPIC/$FOLDER/$NAME/README.md"
echo ""
echo "Next: edit the task README to fill in the description."
