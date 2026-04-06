#!/usr/bin/env bash
# Check which full-pipeline regressions have a recording in ai-builder-recordings.
#
# Queries the remote repo via gh api — no local clone required.
# Exits non-zero if any recordings are missing.
#
# Usage:
#   bash tests/regression/check-recordings-status.sh

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Regressions that intentionally have no recording.
EXCLUDED="infra-smoke goldutil lib fibonacci template-setup"

# ---------------------------------------------------------------------------
# Fetch remote branch list
# ---------------------------------------------------------------------------

BRANCHES=$(gh api repos/cornjacket/ai-builder-recordings/branches --jq '.[].name' 2>/dev/null) || {
    echo "ERROR: gh api call failed. Are you logged in? Run: gh auth login" >&2
    exit 1
}

# ---------------------------------------------------------------------------
# Walk regression directories that have a run.sh (full-pipeline only)
# ---------------------------------------------------------------------------

MISSING=0

printf "%-30s %s\n" "Regression" "Status"
printf "%-30s %s\n" "----------" "------"

for run_sh in "$DIR"/*/run.sh; do
    name="$(basename "$(dirname "$run_sh")")"

    # Skip excluded entries
    if echo "$EXCLUDED" | grep -qw "$name"; then
        continue
    fi

    if echo "$BRANCHES" | grep -qx "$name"; then
        printf "%-30s %s\n" "$name" "✓  recorded"
    else
        printf "%-30s %s\n" "$name" "✗  MISSING"
        MISSING=$((MISSING + 1))
    fi
done

echo ""
if [[ "$MISSING" -gt 0 ]]; then
    echo "$MISSING regression(s) have no recording."
    exit 1
else
    echo "All regressions have recordings."
fi
