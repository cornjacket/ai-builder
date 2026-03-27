#!/usr/bin/env bash
# Advance the pipeline after a leaf task completes.
#
# Performs upward tree traversal: if the completed task is the last at its
# level, marks the parent complete and walks up. Repeats until a next sibling
# is found or the pipeline root boundary is reached.
#
# The pipeline root boundary is detected when the parent directory has no
# task.json (human-owned task — pipeline stops here).
#
# The completed leaf must already be marked [x] before calling this script
# (use on-task-complete.sh to do both in one call).
#
# Usage:
#   advance-pipeline.sh --current <readme> --output-dir <dir> [--epic <epic>]
#
# Stdout:
#   "NEXT <path>" — path to next task README (also written to current-job.txt)
#   "DONE"        — pipeline tree complete
#
# Exit codes:
#   0 — success
#   1 — error

set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPTS_DIR/../../.." && pwd)"
# shellcheck source=task-json-helpers.sh
source "$SCRIPTS_DIR/task-json-helpers.sh"

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
    echo "Usage: advance-pipeline.sh --current <readme> --output-dir <dir> [--epic <epic>]" >&2
    exit 1
fi

# Detect FOLDER (e.g. in-progress) from the current path.
TASKS_DIR="$REPO_ROOT/project/tasks/$EPIC"
current_abs="$(cd "$(dirname "$CURRENT")" && pwd)/$(basename "$CURRENT")"
remaining="${current_abs#${TASKS_DIR}/}"
FOLDER="${remaining%%/*}"
FOLDER_DIR="$TASKS_DIR/$FOLDER"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Return true if a task directory is human-owned (pipeline boundary).
# A directory is human-owned when it has no task.json.
is_human_boundary() {
    local task_dir="$1"
    [[ ! -d "$task_dir" ]] && return 0
    ! is_pipeline_task "$task_dir"
}

# Compute the path of a directory relative to FOLDER_DIR.
# Used to build --parent arguments for task management scripts.
rel_to_folder() {
    echo "${1#${FOLDER_DIR}/}"
}

# ---------------------------------------------------------------------------
# Traversal loop
# ---------------------------------------------------------------------------

current="$(cd "$(dirname "$CURRENT")" && pwd)/$(basename "$CURRENT")"

while true; do
    current_dir="$(dirname "$current")"
    parent_dir="$(dirname "$current_dir")"

    # Read last-task from the current task's task.json
    current_json="$current_dir/task.json"
    last_task="false"
    if [[ -f "$current_json" ]]; then
        last_task="$(json_get "$current_json" "last-task")"
    fi

    if [[ "$last_task" != "true" ]]; then
        # More siblings remain at this level — find the next one.
        parent_rel="$(rel_to_folder "$parent_dir")"
        next=$("$SCRIPTS_DIR/next-subtask.sh" \
            --epic "$EPIC" --folder "$FOLDER" --parent "$parent_rel")
        "$SCRIPTS_DIR/set-current-job.sh" --output-dir "$OUTPUT_DIR" "$next"
        echo "NEXT $next"
        exit 0
    fi

    # Last at this level — need to walk up.

    # If parent is human-owned, we cannot mark it complete; pipeline is done.
    if is_human_boundary "$parent_dir"; then
        echo "DONE"
        exit 0
    fi

    # Mark the parent (composite node) complete and continue walking up.
    grandparent_dir="$(dirname "$parent_dir")"
    parent_name="$(basename "$parent_dir")"
    grandparent_rel="$(rel_to_folder "$grandparent_dir")"

    # If grandparent is human-owned, this is the top-level pipeline node.
    # Defer the directory rename so the orchestrator can flush in-memory state
    # (metrics, README) while task.json paths are still valid. The orchestrator
    # performs the rename as the very last step after all writes are done.
    if is_human_boundary "$grandparent_dir"; then
        "$SCRIPTS_DIR/complete-task.sh" \
            --skip-rename \
            --epic "$EPIC" --folder "$FOLDER" \
            --parent "$grandparent_rel" --name "$parent_name"
        echo "TOP_RENAME_PENDING $parent_dir"
        echo "DONE"
        exit 0
    fi

    "$SCRIPTS_DIR/complete-task.sh" \
        --epic "$EPIC" --folder "$FOLDER" \
        --parent "$grandparent_rel" --name "$parent_name"

    # complete-task.sh renamed parent_dir to X-<parent_name>. Update the path
    # so the next loop iteration can read the README from its new location.
    parent_dir="${grandparent_dir}/X-${parent_name}"

    # Walk up: check if the parent was also the last at its level.
    current="$parent_dir/README.md"
done
