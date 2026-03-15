#!/usr/bin/env bash
# Print the absolute path of the next incomplete subtask README under a
# given parent task, or exit 1 if all subtasks are complete.
#
# Usage:
#   next-subtask.sh --epic <epic> --folder <status> --parent <parent-id-name>
#
# Exit codes:
#   0 — next incomplete subtask found; path printed to stdout
#   1 — all subtasks complete (or no subtasks)

set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPTS_DIR/../../.." && pwd)"

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------

EPIC="main"
FOLDER=""
PARENT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --epic)   EPIC="$2";   shift 2 ;;
        --folder) FOLDER="$2"; shift 2 ;;
        --parent) PARENT="$2"; shift 2 ;;
        *) echo "Unknown flag: $1" >&2; exit 1 ;;
    esac
done

if [[ -z "$FOLDER" || -z "$PARENT" ]]; then
    echo "Usage: next-subtask.sh --folder <status> --parent <parent-id-name> [--epic <epic>]" >&2
    exit 1
fi

PARENT_README="$REPO_ROOT/project/tasks/$EPIC/$FOLDER/$PARENT/README.md"

if [[ ! -f "$PARENT_README" ]]; then
    echo "Parent task not found: project/tasks/$EPIC/$FOLDER/$PARENT" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Find first incomplete subtask
# ---------------------------------------------------------------------------

# Extract the subtask list section and find the first unchecked entry
NEXT_NAME=$(awk '/<!-- subtask-list-start -->/,/<!-- subtask-list-end -->/' "$PARENT_README" \
    | grep '^\- \[ \]' \
    | head -1 \
    | sed 's/^- \[ \] //' \
    | sed 's/^\[\([^]]*\)\](.*/\1/' )  # strip linked format [name](path/) -> name

if [[ -z "$NEXT_NAME" ]]; then
    exit 1
fi

SUBTASK_README="$REPO_ROOT/project/tasks/$EPIC/$FOLDER/$PARENT/$NEXT_NAME/README.md"

if [[ ! -f "$SUBTASK_README" ]]; then
    echo "Subtask directory not found: $NEXT_NAME" >&2
    exit 1
fi

echo "$SUBTASK_README"
