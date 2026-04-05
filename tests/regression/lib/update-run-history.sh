#!/usr/bin/env bash
# Fill in the Gold and Notes columns of the last row in a run-history.md file.
#
# Usage:
#   update-run-history.sh --history <path> --gold pass|fail --notes "<text>"
#
# Overwrites the last data row's Gold and Notes columns in-place. Token-free —
# reads and edits the markdown table directly without AI involvement.
#
# Caller variables (required):
#   --history   path to the run-history.md file
#   --gold      pass or fail
#   --notes     free-text note (reference the triggering task, or a reason)

set -euo pipefail

HISTORY=""
GOLD=""
NOTES=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --history) HISTORY="$2"; shift 2 ;;
        --gold)    GOLD="$2";    shift 2 ;;
        --notes)   NOTES="$2";  shift 2 ;;
        *) echo "Unknown argument: $1" >&2; exit 1 ;;
    esac
done

if [[ -z "$HISTORY" || -z "$GOLD" || -z "$NOTES" ]]; then
    echo "Usage: $0 --history <path> --gold pass|fail --notes \"<text>\"" >&2
    exit 1
fi

if [[ "$GOLD" != "pass" && "$GOLD" != "fail" ]]; then
    echo "Error: --gold must be 'pass' or 'fail'" >&2
    exit 1
fi

if [[ ! -f "$HISTORY" ]]; then
    echo "Error: history file not found: $HISTORY" >&2
    exit 1
fi

# Find the line number of the last data row (starts with |, not a separator line)
LAST_ROW=$(grep -n "^|" "$HISTORY" | grep -v -- "---" | tail -1 | cut -d: -f1)

if [[ -z "$LAST_ROW" ]]; then
    echo "Error: no data rows found in $HISTORY" >&2
    exit 1
fi

# Replace the two trailing empty columns (Gold and Notes) with the provided values.
# Pattern: | | | at end of line → | pass/fail | notes text |
awk -v line="$LAST_ROW" -v gold="$GOLD" -v notes="$NOTES" '
    NR == line {
        sub(/\| *\| *\|[[:space:]]*$/, "| " gold " | " notes " |")
    }
    { print }
' "$HISTORY" > "$HISTORY.tmp" && mv "$HISTORY.tmp" "$HISTORY"

echo "Updated run $LAST_ROW: gold=$GOLD notes=$NOTES"
