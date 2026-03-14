#!/usr/bin/env bash
# Check whether a task README is marked as the last (integration) task.
#
# Reads the Last-task field from the task metadata table.
#
# Usage:
#   is-last-task.sh <task-readme-path>
#
# Exit codes:
#   0 — Last-task: true
#   1 — Last-task: false, field absent, or file not found
#
# Example:
#   if is-last-task.sh project/tasks/main/in-progress/abc123-my-task/xyz-integrate/README.md
#   then echo "integration step"
#   fi

set -euo pipefail

README="${1:-}"

if [[ -z "$README" ]]; then
    echo "Usage: is-last-task.sh <task-readme-path>"
    exit 1
fi

if [[ ! -f "$README" ]]; then
    exit 1
fi

if grep -qE '^\|\s*Last-task\s*\|\s*true\s*\|' "$README"; then
    exit 0
fi

exit 1
