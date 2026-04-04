#!/usr/bin/env bash
# Create a new top-level user-task directory with a user-task-template README.md.
# Updates the status folder's README.md task list.
#
# Usage:
#   new-user-task.sh --epic <epic> --folder <status> --name <task-name> [--id HEX] [--tags <tags>] [--priority <p>]
#
# --id HEX  Use the given 6-char hex string as the task ID instead of generating
#           a random one. Intended for replay regression tests that need to
#           reproduce the exact task directory names from a prior recording.
#
# Priority values: CRITICAL, HIGH, MED, LOW (default: —)
#
# Examples:
#   new-user-task.sh --epic main --folder draft --name my-feature
#   new-user-task.sh --epic main --folder in-progress --name my-feature --priority HIGH
#   new-user-task.sh --epic main --folder in-progress --name my-feature --id 61857e

set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPTS_DIR/../../.." && pwd)"
# shellcheck source=task-id-helpers.sh
source "$SCRIPTS_DIR/task-id-helpers.sh"
TASK_TEMPLATE="$SCRIPTS_DIR/user-task-template.md"

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------

EPIC="main"
FOLDER=""
NAME=""
TAGS="—"
PRIORITY="—"
FIXED_ID=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --epic)     EPIC="$2";     shift 2 ;;
        --folder)   FOLDER="$2";   shift 2 ;;
        --name)     NAME="$2";     shift 2 ;;
        --id)       FIXED_ID="$2"; shift 2 ;;
        --tags)     TAGS="$2";     shift 2 ;;
        --priority) PRIORITY="$2"; shift 2 ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
done

if [[ -z "$FOLDER" || -z "$NAME" ]]; then
    echo "Usage: new-user-task.sh --folder <status> --name <task-name> [--epic <epic>] [--id HEX] [--tags <tags>] [--priority <CRITICAL|HIGH|MED|LOW>]"
    exit 1
fi

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------

STATUS_DIR="$REPO_ROOT/project/tasks/$EPIC/$FOLDER"

if [[ ! -d "$STATUS_DIR" ]]; then
    echo "Status directory not found: $STATUS_DIR"
    exit 1
fi

STATUS="$FOLDER"
CREATED="$(date +%Y-%m-%d)"

# Generate a short unique ID and build the directory name
if [[ -n "$FIXED_ID" ]]; then
    ID="$FIXED_ID"
else
    ID="$(openssl rand -hex 3)"
fi
DIRNAME="$ID-$NAME"

TASK_DIR="$STATUS_DIR/$DIRNAME"
PARENT_README="$STATUS_DIR/README.md"

# ---------------------------------------------------------------------------
# Create task directory and README
# ---------------------------------------------------------------------------

mkdir -p "$TASK_DIR"

sed \
    -e "s/{{NAME}}/$NAME/g" \
    -e "s/{{STATUS}}/$STATUS/g" \
    -e "s/{{EPIC}}/$EPIC/g" \
    -e "s/{{TAGS}}/$TAGS/g" \
    -e "s/{{PRIORITY}}/$PRIORITY/g" \
    -e "s/{{CREATED}}/$CREATED/g" \
    "$TASK_TEMPLATE" > "$TASK_DIR/README.md"

# ---------------------------------------------------------------------------
# Create parent README if it doesn't exist (status directory case)
# ---------------------------------------------------------------------------

if [[ ! -f "$PARENT_README" ]]; then
    cat > "$PARENT_README" << EOF
# $EPIC / $FOLDER

## Tasks

<!-- When a task is finished, run move-task.sh --to complete before moving on. -->
<!-- task-list-start -->
<!-- task-list-end -->
EOF
fi

# ---------------------------------------------------------------------------
# Append to parent README
# ---------------------------------------------------------------------------

if grep -q "<!-- task-list-end -->" "$PARENT_README"; then
    _sed_i "s|<!-- task-list-end -->|- [$DIRNAME]($DIRNAME/)\n<!-- task-list-end -->|" "$PARENT_README"
else
    echo "Warning: no task list markers found in $PARENT_README — add the entry manually."
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

echo "Created user-task: project/tasks/$EPIC/$FOLDER/$DIRNAME/"
echo "Updated:           $PARENT_README"
