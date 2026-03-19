#!/usr/bin/env bash
# Create a new pipeline-subtask directory with a task.json and prose-only README.md.
# Updates the parent task's task.json subtask list.
#
# Used for both pipeline entry points (build-N under a user-task or user-subtask)
# and pipeline-internal nodes (components, integrate, test, etc. under a build-N).
#
# Usage:
#   new-pipeline-subtask.sh --epic <epic> --folder <status> --parent <task> --name <name> [--tags <tags>] [--priority <p>] [--level <TOP|INTERNAL>]
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
# shellcheck source=task-json-helpers.sh
source "$SCRIPTS_DIR/task-json-helpers.sh"

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

PARENT_JSON="$PARENT_DIR/task.json"
PARENT_SHORT_ID="$(get_parent_short_id "$PARENT_DIR")"

# Read NEXT_ID from parent task.json (incrementing the counter in place)
if [[ ! -f "$PARENT_JSON" ]]; then
    echo "Parent task.json not found: $PARENT_JSON"
    exit 1
fi

NEXT_ID="$(get_and_increment_subtask_id "$PARENT_JSON")"
DIRNAME="$PARENT_SHORT_ID-$NEXT_ID-$NAME"

TASK_DIR="$PARENT_DIR/$DIRNAME"

# Extract just the immediate parent name for the parent field
PARENT_NAME="$(basename "$PARENT")"

# ---------------------------------------------------------------------------
# Create subtask directory, task.json, and README
# ---------------------------------------------------------------------------

mkdir -p "$TASK_DIR"

# Write task.json with all structured metadata
python3 - "$TASK_DIR/task.json" "$NAME" "$EPIC" "$PARENT_NAME" "$PRIORITY" "$LEVEL" "$TAGS" <<'EOF'
import sys, json
path, name, epic, parent, priority, level, tags = sys.argv[1:]
data = {
    "task-type": "PIPELINE-SUBTASK",
    "status": "—",
    "epic": epic,
    "parent": parent,
    "tags": tags,
    "priority": priority,
    "next-subtask-id": "0000",
    "complexity": "—",
    "level": level,
    "last-task": False,
    "stop-after": False,
    "components": [],
    "subtasks": []
}
with open(path, 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
EOF

# Write prose-only README from template (only {{NAME}} substitution needed)
sed -e "s/{{NAME}}/$NAME/g" "$TASK_TEMPLATE" > "$TASK_DIR/README.md"

# ---------------------------------------------------------------------------
# Append subtask entry to parent task.json
# ---------------------------------------------------------------------------

json_append_subtask "$PARENT_JSON" "$DIRNAME"

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

echo "Created pipeline-subtask: project/tasks/$EPIC/$FOLDER/$PARENT/$DIRNAME/"
echo "Updated:                  $PARENT_JSON"
