#!/usr/bin/env bash
# Create a Level:TOP pipeline-subtask as the entry point for a pipeline build run.
#
# This is the canonical way to create a pipeline build task. It wraps
# new-pipeline-subtask.sh with --level TOP enforced and outputs the README
# path so it can be piped directly to set-current-job.sh.
#
# Usage:
#   new-pipeline-build.sh --epic <epic> --folder <status> --parent <task> [--name <name>] [--spec-file <path>]
#
# --name defaults to "build-1" if not supplied.
# --spec-file copies the given file to the entry README and extracts goal/context
#   into task.json. Use this in reset.sh so task.json is populated in one step.
#
# Example (Oracle interactive):
#   README=$(new-pipeline-build.sh --epic main --folder in-progress --parent my-project | grep "^README:" | awk '{print $2}')
#   # write spec to $README, then run orchestrator
#
# Example (reset.sh):
#   new-pipeline-build.sh --epic main --folder in-progress --parent my-project --spec-file "$DIR/build-spec.md"

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
SPEC_FILE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --epic)      EPIC="$2";      shift 2 ;;
        --folder)    FOLDER="$2";    shift 2 ;;
        --parent)    PARENT="$2";    shift 2 ;;
        --name)      NAME="$2";      shift 2 ;;
        --spec-file) SPEC_FILE="$2"; shift 2 ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
done

if [[ -z "$FOLDER" || -z "$PARENT" ]]; then
    echo "Usage: new-pipeline-build.sh --folder <status> --parent <task> [--epic <epic>] [--name <name>] [--spec-file <path>]"
    exit 1
fi

if [[ -n "$SPEC_FILE" && ! -f "$SPEC_FILE" ]]; then
    echo "ERROR: --spec-file not found: $SPEC_FILE"
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
# If --spec-file provided: copy spec to README and extract goal/context into
# task.json. Without --spec-file the README is left as the generated template
# and the caller is responsible for writing the spec and populating task.json.
# ---------------------------------------------------------------------------

TASK_JSON="$REPO_ROOT/$CREATED_REL/task.json"

if [[ -n "$SPEC_FILE" ]]; then
    cp "$SPEC_FILE" "$README_PATH"
    echo "    spec:   $README_PATH"

    python3 - "$README_PATH" "$TASK_JSON" <<'PYEOF'
import sys, json, re

readme_path, task_json_path = sys.argv[1], sys.argv[2]
readme = open(readme_path).read()
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
    echo "    task.json updated with goal/context"
fi
