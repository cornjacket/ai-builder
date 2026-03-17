#!/usr/bin/env bash
# Check if a pipeline-subtask's Stop-after field is true.
#
# Usage:
#   check-stop-after.sh <task-readme-path>
#
# Exit codes:
#   0 — Stop-after is true
#   1 — Stop-after is false, missing, or unset
#   2 — usage error

set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: check-stop-after.sh <task-readme-path>" >&2
    exit 2
fi

if [[ ! -f "$1" ]]; then
    echo "File not found: $1" >&2
    exit 2
fi

grep -qE "^\| *Stop-after *\| *true *\|" "$1" && exit 0 || exit 1
