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

PARENT_JSON="$PARENT_DIR/task.json"
PARENT_README="$PARENT_DIR/README.md"
PARENT_SHORT_ID="$(get_parent_short_id "$PARENT_DIR")"

# Read NEXT_ID from parent task.json (pipeline parent) or README (user-task parent).
# Pipeline builds (Level:TOP) have user tasks as parents — no task.json there.
if [[ -f "$PARENT_JSON" ]]; then
    NEXT_ID="$(get_and_increment_subtask_id "$PARENT_JSON")"
    PARENT_HAS_JSON=true
elif [[ -f "$PARENT_README" ]]; then
    NEXT_ID="$(get_next_subtask_id "$PARENT_README")"
    if [[ -z "$NEXT_ID" ]]; then
        NEXT_ID="0000"
        _sed_i "s/| Priority *|[^|]*|/&\n| Next-subtask-id | 0000               |/" "$PARENT_README"
    fi
    increment_subtask_id "$PARENT_README"
    PARENT_HAS_JSON=false
else
    echo "Parent has neither task.json nor README.md: $PARENT_DIR"
    exit 1
fi

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
from datetime import date
path, name, epic, parent, priority, level, tags = sys.argv[1:]
data = {
    "task-type": "PIPELINE-SUBTASK",
    "status": "—",
    "epic": epic,
    "parent": parent,
    "tags": tags,
    "priority": priority,
    "created_at": date.today().isoformat(),
    "completed_at": None,
    "next-subtask-id": "0000",
    "complexity": "—",
    "level": level,
    "depth": 0,
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
# Register subtask in parent (task.json for pipeline parents, README for user-task parents)
# ---------------------------------------------------------------------------

if [[ "$PARENT_HAS_JSON" == true ]]; then
    json_append_subtask "$PARENT_JSON" "$DIRNAME"
    UPDATED="$PARENT_JSON"
else
    if grep -q "<!-- subtask-list-end -->" "$PARENT_README"; then
        _sed_i "s|<!-- subtask-list-end -->|- [ ] [$DIRNAME]($DIRNAME/)\n<!-- subtask-list-end -->|" "$PARENT_README"
    fi
    UPDATED="$PARENT_README"
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

echo "Created pipeline-subtask: project/tasks/$EPIC/$FOLDER/$PARENT/$DIRNAME/"
echo "Updated:                  $UPDATED"
