#!/usr/bin/env bash
# Mark a subtask as wont-do.
#
# Sets Status to 'wont-do' in the subtask's README and removes its entry
# from the parent README's subtask list. The subtask directory is kept in
# place for reference.
#
# Usage:
#   wont-do-subtask.sh --epic <epic> --folder <status> --parent <task> --name <subtask>
#
# Examples:
#   wont-do-subtask.sh --epic main --folder in-progress --parent my-task --name my-subtask

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

if [[ -z "$FOLDER" || -z "$PARENT" || -z "$NAME" ]]; then
    echo "Usage: wont-do-subtask.sh --folder <status> --parent <task> --name <subtask> [--epic <epic>]"
    exit 1
fi

PARENT_README="$REPO_ROOT/project/tasks/$EPIC/$FOLDER/$PARENT/README.md"
SUBTASK_README="$REPO_ROOT/project/tasks/$EPIC/$FOLDER/$PARENT/$NAME/README.md"

if [[ ! -f "$PARENT_README" ]]; then
    echo "Parent task not found: project/tasks/$EPIC/$FOLDER/$PARENT"
    exit 1
fi
if [[ ! -f "$SUBTASK_README" ]]; then
    echo "Subtask not found: project/tasks/$EPIC/$FOLDER/$PARENT/$NAME"
    exit 1
fi

# ---------------------------------------------------------------------------
# Set Status to wont-do in subtask README
# ---------------------------------------------------------------------------

sed -i '' "s/| Status *|[^|]*|/| Status | wont-do |/" "$SUBTASK_README"

# ---------------------------------------------------------------------------
# Remove entry from parent README subtask list (any format, any check state)
# ---------------------------------------------------------------------------

# Linked format:  - [ ] [NAME](path/)  or  - [x] [NAME](path/)
sed -i '' "/- \[.\] \[$NAME\]($NAME\/)/d" "$PARENT_README"
# Plain format:   - [ ] NAME  or  - [x] NAME
sed -i '' "/- \[.\] $NAME$/d" "$PARENT_README"

echo "Marked wont-do: $NAME"
echo "Updated:        $PARENT_README"
