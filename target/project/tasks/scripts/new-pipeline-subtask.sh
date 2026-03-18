#!/usr/bin/env bash
# Create a new pipeline-subtask directory with a pipeline-build-template README.md.
# Updates the parent task's README.md subtask list.
#
# Used for both pipeline entry points (build-N under a user-task or user-subtask)
# and pipeline-internal nodes (components, integrate, test, etc. under a build-N).
#
# Usage:
#   new-pipeline-subtask.sh --epic <epic> --folder <status> --parent <task> --name <name> [--tags <tags>] [--priority <p>]
#
# Priority values: CRITICAL, HIGH, MED, LOW (default: —)
#
# Examples:
#   new-pipeline-subtask.sh --epic main --folder in-progress --parent my-project --name build-1 --level TOP
#   new-pipeline-subtask.sh --epic main --folder in-progress --parent my-project/build-1 --name auth-component

set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPTS_DIR/../../.." && pwd)"
TASK_TEMPLATE="$SCRIPTS_DIR/pipeline-build-template.md"
# shellcheck source=task-id-helpers.sh
source "$SCRIPTS_DIR/task-id-helpers.sh"

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------

EPIC="main"
FOLDER=""
PARENT=""
NAME=""
TAGS="—"
PRIORITY="—"
LEVEL="INTERNAL"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --epic)     EPIC="$2";     shift 2 ;;
        --folder)   FOLDER="$2";   shift 2 ;;
        --parent)   PARENT="$2";   shift 2 ;;
        --name)     NAME="$2";     shift 2 ;;
        --tags)     TAGS="$2";     shift 2 ;;
        --priority) PRIORITY="$2"; shift 2 ;;
        --level)    LEVEL="$2";    shift 2 ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
done

if [[ -z "$FOLDER" || -z "$PARENT" || -z "$NAME" ]]; then
    echo "Usage: new-pipeline-subtask.sh --folder <status> --parent <task> --name <name> [--epic <epic>] [--tags <tags>] [--priority <CRITICAL|HIGH|MED|LOW>] [--level <TOP|INTERNAL>]"
    exit 1
fi

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------

PARENT_DIR="$REPO_ROOT/project/tasks/$EPIC/$FOLDER/$PARENT"

if [[ ! -d "$PARENT_DIR" ]]; then
    echo "Parent directory not found: $PARENT_DIR"
    exit 1
fi

# For pipeline-internal nodes the name is typically descriptive (e.g. build-1,
# auth-component) rather than id-prefixed. Use incremental IDs for consistency.
PARENT_README="$PARENT_DIR/README.md"
PARENT_SHORT_ID="$(get_parent_short_id "$PARENT_DIR")"
NEXT_ID="$(get_next_subtask_id "$PARENT_README")"
# Default to 0000 and add the field if the parent predates the Next-subtask-id convention
if [[ -z "$NEXT_ID" ]]; then
    NEXT_ID="0000"
    sed -i '' "s/| Priority *|[^|]*|/&\n| Next-subtask-id | 0000               |/" "$PARENT_README"
fi
DIRNAME="$PARENT_SHORT_ID-$NEXT_ID-$NAME"

TASK_DIR="$PARENT_DIR/$DIRNAME"

# Extract just the immediate parent name for the Parent field
PARENT_NAME="$(basename "$PARENT")"

# ---------------------------------------------------------------------------
# Create subtask directory and README
# ---------------------------------------------------------------------------

mkdir -p "$TASK_DIR"

sed \
    -e "s/{{NAME}}/$NAME/g" \
    -e "s/{{EPIC}}/$EPIC/g" \
    -e "s/{{TAGS}}/$TAGS/g" \
    -e "s/{{PARENT}}/$PARENT_NAME/g" \
    -e "s/{{PRIORITY}}/$PRIORITY/g" \
    -e "s/{{LEVEL}}/$LEVEL/g" \
    "$TASK_TEMPLATE" > "$TASK_DIR/README.md"

# ---------------------------------------------------------------------------
# Append to parent README subtask list
# ---------------------------------------------------------------------------

if grep -q "<!-- subtask-list-end -->" "$PARENT_README"; then
    sed -i '' "s|<!-- subtask-list-end -->|- [ ] [$DIRNAME]($DIRNAME/)\n<!-- subtask-list-end -->|" "$PARENT_README"
else
    echo "Warning: no subtask list markers found in $PARENT_README — add the entry manually."
fi

increment_subtask_id "$PARENT_README"

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

echo "Created pipeline-subtask: project/tasks/$EPIC/$FOLDER/$PARENT/$DIRNAME/"
echo "Updated:                  $PARENT_README"
