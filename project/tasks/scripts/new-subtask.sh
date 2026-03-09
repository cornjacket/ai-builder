#!/usr/bin/env bash
# Create a subtask directory under an existing task.
# Updates the parent task README.md subtask list.
#
# Usage:
#   new-subtask.sh --epic <epic> --folder <status> --parent <task> --name <subtask> [--tags <tags>]
#
# Example:
#   new-subtask.sh --epic main --folder draft \
#       --parent create-project-management-system --name write-scripts

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
TAGS="—"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --epic)   EPIC="$2";   shift 2 ;;
        --folder) FOLDER="$2"; shift 2 ;;
        --parent) PARENT="$2"; shift 2 ;;
        --name)   NAME="$2";   shift 2 ;;
        --tags)   TAGS="$2";   shift 2 ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
done

if [[ -z "$FOLDER" || -z "$PARENT" || -z "$NAME" ]]; then
    echo "Usage: new-subtask.sh --folder <status> --parent <task> --name <subtask> [--epic <epic>] [--tags <tags>]"
    exit 1
fi

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PARENT_DIR="$REPO_ROOT/project/tasks/$EPIC/$FOLDER/$PARENT"
SUBTASK_DIR="$PARENT_DIR/$NAME"
PARENT_README="$PARENT_DIR/README.md"

if [[ ! -d "$PARENT_DIR" ]]; then
    echo "Parent task not found: project/tasks/$EPIC/$FOLDER/$PARENT"
    exit 1
fi

if [[ -d "$SUBTASK_DIR" ]]; then
    echo "Subtask already exists: project/tasks/$EPIC/$FOLDER/$PARENT/$NAME"
    exit 1
fi

# ---------------------------------------------------------------------------
# Create subtask directory and README
# ---------------------------------------------------------------------------

mkdir -p "$SUBTASK_DIR"

cat > "$SUBTASK_DIR/README.md" << EOF
# Task: $NAME

| Field  | Value    |
|--------|----------|
| Status | $FOLDER  |
| Epic   | $EPIC    |
| Tags   | $TAGS    |
| Parent | $PARENT  |

## Description

_To be written._

## Subtasks

_None._

## Notes

_None._
EOF

# ---------------------------------------------------------------------------
# Update parent README: replace "_None._" with subtask list entry,
# or append to existing subtask list
# ---------------------------------------------------------------------------

if grep -q "^_None\._$" "$PARENT_README"; then
    # First subtask — replace the placeholder
    sed -i '' "s|^_None\._$|- [ ] [$NAME]($NAME/)|" "$PARENT_README"
else
    # Additional subtask — append after the last subtask entry
    sed -i '' "/^- \[ \] \[.*\]\(.*\)$/a\\
- [ ] [$NAME]($NAME/)" "$PARENT_README"
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

echo "Created: project/tasks/$EPIC/$FOLDER/$PARENT/$NAME/"
echo "         project/tasks/$EPIC/$FOLDER/$PARENT/$NAME/README.md"
echo "Updated: project/tasks/$EPIC/$FOLDER/$PARENT/README.md"
