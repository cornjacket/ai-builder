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
# Example:
#   README=$(new-pipeline-build.sh --epic main --folder in-progress --parent my-project | grep "^README:" | awk '{print $2}')
#   set-current-job.sh --output-dir <output-dir> "$README"

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
# The parent already exists with its spec written before this script runs.
# Use direct path construction — the parent dir is known from FOLDER + PARENT.
# ---------------------------------------------------------------------------

TASK_JSON="$REPO_ROOT/project/tasks/$EPIC/$FOLDER/$PARENT/task.json"
PARENT_README="$REPO_ROOT/project/tasks/$EPIC/$FOLDER/$PARENT/README.md"

# Note: TASK_JSON for the new subtask, not the parent
TASK_JSON="$REPO_ROOT/$CREATED_REL/task.json"

if [[ -f "$PARENT_README" ]]; then
    python3 - "$PARENT_README" "$TASK_JSON" <<'PYEOF'
import sys, json, re

parent_readme_path, task_json_path = sys.argv[1], sys.argv[2]

try:
    readme = open(parent_readme_path).read()
except Exception:
    sys.exit(0)

goal_match = re.search(r'## Goal\s*\n+(.*?)(?=\n## |\Z)', readme, re.DOTALL)
context_match = re.search(r'## Context\s*\n+(.*?)(?=\n## |\Z)', readme, re.DOTALL)

goal = goal_match.group(1).strip() if goal_match else ""
context = context_match.group(1).strip() if context_match else ""

if context == "_To be written._":
    context = ""
if goal == "_To be written._":
    goal = ""

if not goal and not context:
    sys.exit(0)

try:
    data = json.loads(open(task_json_path).read())
except Exception:
    sys.exit(0)

if goal:
    data["goal"] = goal
if context:
    data["context"] = context

with open(task_json_path, 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
PYEOF
    echo "    task.json: goal/context read from parent README"
else
    echo "    task.json: parent README not found; goal/context not set"
fi
