#!/usr/bin/env bash
# Check if a pipeline-subtask's Level field is TOP.
#
# Usage:
#   is-top-level.sh <task-readme-path>
#
# Exit codes:
#   0 — Level is TOP
#   1 — Level is INTERNAL, missing, or unset
#   2 — usage error

set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: is-top-level.sh <task-readme-path>" >&2
    exit 2
fi

if [[ ! -f "$1" ]]; then
    echo "File not found: $1" >&2
    exit 2
fi

grep -qE "^\| *Level *\| *TOP *\|" "$1" && exit 0 || exit 1
