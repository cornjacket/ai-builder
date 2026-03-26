#!/usr/bin/env bash
# Check if a pipeline-subtask's stop-after field is true.
#
# Reads stop-after from task.json in the same directory as the argument.
# The argument may be a README path or a task directory path.
#
# Usage:
#   check-stop-after.sh <task-readme-path-or-task-dir>
#
# Exit codes:
#   0 — stop-after is true
#   1 — stop-after is false, missing, or unset
#   2 — usage error

set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=task-json-helpers.sh
source "$SCRIPTS_DIR/task-json-helpers.sh"

if [[ $# -ne 1 ]]; then
    echo "Usage: check-stop-after.sh <task-readme-path-or-task-dir>" >&2
    exit 2
fi

ARG="$1"

# Resolve to the task directory
if [[ -f "$ARG" ]]; then
    TASK_DIR="$(dirname "$ARG")"
elif [[ -d "$ARG" ]]; then
    TASK_DIR="$ARG"
else
    echo "Not found: $ARG" >&2
    exit 2
fi

JSON_FILE="$TASK_DIR/task.json"

if [[ ! -f "$JSON_FILE" ]]; then
    exit 1
fi

val="$(json_get "$JSON_FILE" "stop-after")"
[[ "$val" == "true" ]] && exit 0 || exit 1
