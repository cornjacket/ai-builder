#!/usr/bin/env bash
# Check whether all subtasks of a parent task are marked [x] complete.
#
# Reads the subtask list (between subtask-list-start and subtask-list-end
# markers) in the parent task's README.md and checks for any remaining
# unchecked items.
#
# Usage:
#   subtasks-complete.sh --epic <epic> --folder <status> --parent <parent-task>
#
# Exit codes:
#   0 — all subtasks complete (or no subtasks exist)
#   1 — one or more subtasks remain incomplete
#
# Example:
#   subtasks-complete.sh --epic main --folder in-progress --parent abc123-my-task
#   if subtasks-complete.sh ...; then echo "all done"; fi

set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPTS_DIR/../../.." && pwd)"

EPIC="main"
FOLDER=""
PARENT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --epic)   EPIC="$2";   shift 2 ;;
        --folder) FOLDER="$2"; shift 2 ;;
        --parent) PARENT="$2"; shift 2 ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
done

if [[ -z "$FOLDER" || -z "$PARENT" ]]; then
    echo "Usage: subtasks-complete.sh --epic <epic> --folder <status> --parent <parent-task>"
    exit 1
fi

PARENT_README="$REPO_ROOT/project/tasks/$EPIC/$FOLDER/$PARENT/README.md"

if [[ ! -f "$PARENT_README" ]]; then
    echo "Parent task not found: project/tasks/$EPIC/$FOLDER/$PARENT"
    exit 1
fi

# Extract the subtask list section and check for any unchecked items
incomplete=$(awk '/<!-- subtask-list-start -->/,/<!-- subtask-list-end -->/' "$PARENT_README" \
    | grep -c '^\- \[ \]' || true)

if [[ "$incomplete" -gt 0 ]]; then
    exit 1
fi

exit 0
