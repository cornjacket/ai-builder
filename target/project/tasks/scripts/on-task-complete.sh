#!/usr/bin/env bash
# Complete a pipeline leaf task and advance the pipeline.
#
# Wraps three operations into a single call:
#   1. complete-task.sh    — marks the leaf [x] in its parent's subtask list
#   2. check-stop-after.sh — checks if a human review pause is requested
#   3. advance-pipeline.sh — tree traversal to find the next task or signal done
#
# Usage:
#   on-task-complete.sh --current <readme> --output-dir <dir> [--epic <epic>]
#
# Stdout (one of):
#   "NEXT <path>"  — path to next task README (also written to current-job.txt)
#   "DONE"         — pipeline tree complete
#   "STOP_AFTER"   — Stop-after flag set; human review required before continuing
#
# Exit codes:
#   0 — success
#   1 — error

set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPTS_DIR/../../.." && pwd)"

CURRENT=""
OUTPUT_DIR=""
EPIC="main"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --current)    CURRENT="$2";    shift 2 ;;
        --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
        --epic)       EPIC="$2";       shift 2 ;;
        *) echo "Unknown flag: $1" >&2; exit 1 ;;
    esac
done

if [[ -z "$CURRENT" || -z "$OUTPUT_DIR" ]]; then
    echo "Usage: on-task-complete.sh --current <readme> --output-dir <dir> [--epic <epic>]" >&2
    exit 1
fi

# Detect FOLDER (e.g. in-progress) from the current path.
# If the task directory was already renamed with an X- prefix (e.g. by an agent
# that called complete-task.sh directly), detect that and skip the completion step.
TASKS_DIR="$REPO_ROOT/project/tasks/$EPIC"

_given_dir="$(dirname "$CURRENT")"
_given_name="$(basename "$_given_dir")"
_given_parent="$(dirname "$_given_dir")"
ALREADY_COMPLETE=false

if [[ -d "$_given_dir" ]]; then
    current="$(cd "$_given_dir" && pwd)/$(basename "$CURRENT")"
elif [[ -d "$_given_parent/X-$_given_name" ]]; then
    current="$(cd "$_given_parent/X-$_given_name" && pwd)/$(basename "$CURRENT")"
    ALREADY_COMPLETE=true
else
    echo "Task not found: $CURRENT" >&2
    exit 2
fi

remaining="${current#${TASKS_DIR}/}"
FOLDER="${remaining%%/*}"
FOLDER_DIR="$TASKS_DIR/$FOLDER"

# ---------------------------------------------------------------------------
# 1. Mark the leaf complete (skip if already renamed by a prior complete-task.sh call)
# ---------------------------------------------------------------------------

current_dir="$(dirname "$current")"
current_name="$(basename "$current_dir")"
parent_dir="$(dirname "$current_dir")"
parent_rel="${parent_dir#${FOLDER_DIR}/}"

if [[ "$ALREADY_COMPLETE" == false ]]; then
    "$SCRIPTS_DIR/complete-task.sh" \
        --epic "$EPIC" --folder "$FOLDER" \
        --parent "$parent_rel" --name "$current_name"
    # complete-task.sh renames the directory to X-<name>; update current accordingly.
    current="${parent_dir}/X-${current_name}/$(basename "$current")"
fi

# ---------------------------------------------------------------------------
# 2. Check Stop-after
# ---------------------------------------------------------------------------

if "$SCRIPTS_DIR/check-stop-after.sh" "$current"; then
    echo "STOP_AFTER"
    exit 0
fi

# ---------------------------------------------------------------------------
# 3. Advance the pipeline
# ---------------------------------------------------------------------------

"$SCRIPTS_DIR/advance-pipeline.sh" \
    --current "$current" \
    --output-dir "$OUTPUT_DIR" \
    --epic "$EPIC"
