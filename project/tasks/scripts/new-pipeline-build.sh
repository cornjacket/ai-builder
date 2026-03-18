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
