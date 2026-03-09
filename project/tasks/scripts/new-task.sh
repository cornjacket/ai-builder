#!/usr/bin/env bash
# Create a new task or subtask directory with a template README.md.
# Updates the parent directory's README.md task list.
#
# The parent of any task is always its containing directory:
#   - Top-level task: parent = project/tasks/<epic>/<folder>/
#   - Subtask:        parent = project/tasks/<epic>/<folder>/<parent-task>/
#
# Usage:
#   new-task.sh --epic <epic> --folder <status> --name <task-name> [--tags <tags>] [--priority <p>]
#   new-task.sh --epic <epic> --folder <status> --parent <task> --name <name> [--tags <tags>] [--priority <p>]
#
# Priority values: CRITICAL, HIGH, MED, LOW (default: —)
#
# Examples:
#   new-task.sh --epic main --folder draft --name my-feature
#   new-task.sh --epic main --folder in-progress --parent my-feature --name my-subtask --priority HIGH

set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPTS_DIR/../../.." && pwd)"
TEMPLATE="$SCRIPTS_DIR/task-template.md"

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------

EPIC="main"
FOLDER=""
PARENT=""
NAME=""
TAGS="—"
PRIORITY="—"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --epic)     EPIC="$2";     shift 2 ;;
        --folder)   FOLDER="$2";   shift 2 ;;
        --parent)   PARENT="$2";   shift 2 ;;
        --name)     NAME="$2";     shift 2 ;;
        --tags)     TAGS="$2";     shift 2 ;;
        --priority) PRIORITY="$2"; shift 2 ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
done

if [[ -z "$FOLDER" || -z "$NAME" ]]; then
    echo "Usage: new-task.sh --folder <status> --name <task-name> [--epic <epic>] [--parent <parent-task>] [--tags <tags>] [--priority <CRITICAL|HIGH|MED|LOW>]"
    exit 1
fi

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------

STATUS_DIR="$REPO_ROOT/project/tasks/$EPIC/$FOLDER"

if [[ -n "$PARENT" ]]; then
    PARENT_DIR="$STATUS_DIR/$PARENT"
    PARENT_FIELD="$PARENT"
else
    PARENT_DIR="$STATUS_DIR"
    PARENT_FIELD="—"
fi

# Generate a short unique ID and build the directory name
ID="$(openssl rand -hex 3)"
DIRNAME="$ID-$NAME"

TASK_DIR="$PARENT_DIR/$DIRNAME"
PARENT_README="$PARENT_DIR/README.md"

if [[ ! -d "$PARENT_DIR" ]]; then
    echo "Parent directory not found: $PARENT_DIR"
    exit 1
fi

# ---------------------------------------------------------------------------
# Create task directory and README
# ---------------------------------------------------------------------------

mkdir -p "$TASK_DIR"

sed \
    -e "s/{{NAME}}/$NAME/g" \
    -e "s/{{FOLDER}}/$FOLDER/g" \
    -e "s/{{EPIC}}/$EPIC/g" \
    -e "s/{{TAGS}}/$TAGS/g" \
    -e "s/{{PARENT}}/$PARENT_FIELD/g" \
    -e "s/{{PRIORITY}}/$PRIORITY/g" \
    "$TEMPLATE" > "$TASK_DIR/README.md"

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
# Append to parent README using whichever marker is present
# ---------------------------------------------------------------------------

if grep -q "<!-- subtask-list-end -->" "$PARENT_README"; then
    sed -i '' "s|<!-- subtask-list-end -->|- [ ] [$DIRNAME]($DIRNAME/)\n<!-- subtask-list-end -->|" "$PARENT_README"
elif grep -q "<!-- task-list-end -->" "$PARENT_README"; then
    sed -i '' "s|<!-- task-list-end -->|- [$DIRNAME]($DIRNAME/)\n<!-- task-list-end -->|" "$PARENT_README"
else
    echo "Warning: no task list markers found in $PARENT_README — add the entry manually."
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

if [[ -n "$PARENT" ]]; then
    echo "Created subtask: project/tasks/$EPIC/$FOLDER/$PARENT/$DIRNAME/"
else
    echo "Created task:    project/tasks/$EPIC/$FOLDER/$DIRNAME/"
fi
echo "Updated:         $PARENT_README"
