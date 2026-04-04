#!/usr/bin/env bash
# Create a Level:TOP pipeline-subtask as the entry point for a pipeline build run.
#
# This is the canonical way to create a pipeline build task. It wraps
# new-pipeline-subtask.sh with --level TOP enforced and outputs the README
# path so it can be piped directly to set-current-job.sh.
#
# Usage:
#   new-pipeline-build.sh --epic <epic> --folder <status> --parent <task> [--name <name>]
#
# --name defaults to "build-1" if not supplied.
#
# goal and context are read automatically from the parent task's README.
# Write the spec into the parent USER-TASK before calling this script.
#
# Example:
#   new-pipeline-build.sh --epic main --folder in-progress --parent my-project

set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPTS_DIR/../../.." && pwd)"

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------

EPIC="main"
FOLDER=""
PARENT=""
NAME="build-1"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --epic)   EPIC="$2";   shift 2 ;;
        --folder) FOLDER="$2"; shift 2 ;;
        --parent) PARENT="$2"; shift 2 ;;
        --name)   NAME="$2";   shift 2 ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
done

if [[ -z "$FOLDER" || -z "$PARENT" ]]; then
    echo "Usage: new-pipeline-build.sh --folder <status> --parent <task> [--epic <epic>] [--name <name>]"
    exit 1
fi

# ---------------------------------------------------------------------------
# Delegate to new-pipeline-subtask.sh with --level TOP
# ---------------------------------------------------------------------------

OUTPUT=$("$SCRIPTS_DIR/new-pipeline-subtask.sh" \
    --epic    "$EPIC" \
    --folder  "$FOLDER" \
    --parent  "$PARENT" \
    --name    "$NAME" \
    --level   TOP)

echo "$OUTPUT"

# Extract the created directory path and derive the README path
CREATED_REL=$(echo "$OUTPUT" | grep "^Created pipeline-subtask:" | sed 's/^Created pipeline-subtask: *//' | sed 's|/$||')
README_PATH="$REPO_ROOT/$CREATED_REL/README.md"
echo "README:                   $README_PATH"

# ---------------------------------------------------------------------------
# Read goal/context from the parent USER-TASK README and write to task.json.
# The parent already exists with its spec written before this script runs —
# no timing issue.
# ---------------------------------------------------------------------------

TASK_JSON="$REPO_ROOT/$CREATED_REL/task.json"

# Find the parent task directory. Matches both the exact full name (e.g.
# "a3f2c1-my-task" passed as PARENT) and the suffix pattern (e.g. "my-task"
# passed as PARENT, matching "a3f2c1-my-task"). Exact match is checked first
# so a full-name argument always wins over a coincidental suffix match.
PARENT_DIR=$(find "$REPO_ROOT/project/tasks/$EPIC" -maxdepth 2 -type d \( -name "$PARENT" -o -name "*-$PARENT" \) | head -1)
PARENT_README=""
if [[ -n "$PARENT_DIR" ]]; then
    PARENT_README="$PARENT_DIR/README.md"
fi

if [[ -n "$PARENT_README" && -f "$PARENT_README" ]]; then
    python3 - "$PARENT_README" "$TASK_JSON" <<'PYEOF'
import sys, json, re

parent_readme_path, task_json_path = sys.argv[1], sys.argv[2]
readme = open(parent_readme_path).read()
data = json.loads(open(task_json_path).read())

for field, label in (("goal", "Goal"), ("context", "Context")):
    m = re.search(rf'## {label}\s*\n+(.*?)(?=\n## |\Z)', readme, re.DOTALL)
    if m:
        text = m.group(1).strip()
        if text and text != "_To be written._":
            data[field] = text

with open(task_json_path, 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
PYEOF
    echo "    task.json: goal/context read from parent README"
else
    echo "    task.json: parent README not found; goal/context not set"
fi
