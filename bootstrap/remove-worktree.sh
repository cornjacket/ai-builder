#!/usr/bin/env bash
# Remove a git worktree and its branch atomically.
#
# Must be run from the main worktree. Fetches remote state before acting.
#
# Before removing, verifies that the branch has been merged by checking:
#   1. gh pr list --state merged --head <branch>  (primary — works for squash/rebase PRs)
#   2. Absence of origin/<branch> after git fetch --prune  (fallback when gh unavailable)
#
# If neither check can confirm the branch is merged, the operation is refused.
# This prevents data loss from accidentally removing unmerged work.
#
# Both the worktree directory and the local branch are always removed together
# (atomic — no partial state). The remote branch is also deleted if it still exists.
#
# Run from inside the main worktree (e.g., main/).
#
# Usage:
#   remove-worktree.sh <branch-name>
#
# Example:
#   remove-worktree.sh feat-x

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/../.." && pwd)"

BRANCH=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -*) echo "Unknown flag: $1"; exit 1 ;;
        *)  BRANCH="$1"; shift ;;
    esac
done

if [[ -z "$BRANCH" ]]; then
    echo "Usage: remove-worktree.sh <branch-name>"
    exit 1
fi

if [[ "$BRANCH" == "main" ]]; then
    echo "ERROR: cannot remove the main worktree."
    exit 1
fi

# ---------------------------------------------------------------------------
# Guard: must be run from the main worktree
# ---------------------------------------------------------------------------

CURRENT_BRANCH=$(git -C "$WORKSPACE/main" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
if [[ "$CURRENT_BRANCH" != "main" ]]; then
    echo "ERROR: workflow scripts must be run from the 'main' worktree."
    echo "       The main worktree is currently on branch '$CURRENT_BRANCH'."
    echo "       Switch to main: git -C $WORKSPACE/main checkout main"
    exit 1
fi

# ---------------------------------------------------------------------------
# Fetch remote state (also prunes stale remote-tracking refs)
# ---------------------------------------------------------------------------

echo "Fetching remote state..."
git -C "$WORKSPACE/main" fetch --prune origin

# ---------------------------------------------------------------------------
# Verify worktree exists
# ---------------------------------------------------------------------------

TARGET="$WORKSPACE/$BRANCH"

if [[ ! -d "$TARGET" ]]; then
    echo "ERROR: worktree not found: $TARGET"
    exit 1
fi

# ---------------------------------------------------------------------------
# Verify the branch is merged before removing anything
# ---------------------------------------------------------------------------

MERGED=false

if command -v gh &>/dev/null; then
    # Primary: check whether a merged PR exists for this branch
    MERGED_COUNT=$(gh pr list --state merged --head "$BRANCH" --json number --jq 'length' 2>/dev/null || echo "0")
    if [[ "$MERGED_COUNT" -gt 0 ]]; then
        MERGED=true
    else
        echo "ERROR: no merged PR found for branch '$BRANCH' (checked via gh)."
        echo "       Merge the branch first, then re-run this script."
        exit 1
    fi
else
    # Fallback: remote branch absence after fetch --prune implies it was merged
    # and deleted on the remote. Use only when gh is unavailable.
    if ! git -C "$WORKSPACE/main" show-ref --quiet "refs/remotes/origin/$BRANCH"; then
        echo "WARNING: gh CLI not available; inferring merge from remote branch absence."
        MERGED=true
    else
        echo "ERROR: cannot verify branch '$BRANCH' is merged."
        echo "       Install gh (GitHub CLI) for reliable merge detection, or"
        echo "       merge the branch and ensure the remote branch is deleted."
        exit 1
    fi
fi

# ---------------------------------------------------------------------------
# Remove worktree and branch atomically
# ---------------------------------------------------------------------------

echo "Branch '$BRANCH' confirmed merged — removing worktree and branch..."

git -C "$WORKSPACE/main" worktree remove "$TARGET"
git -C "$WORKSPACE/main" branch -D "$BRANCH"

if git -C "$WORKSPACE/main" show-ref --quiet "refs/remotes/origin/$BRANCH"; then
    echo "Deleting remote branch 'origin/$BRANCH'..."
    git -C "$WORKSPACE/main" push origin --delete "$BRANCH"
fi

echo ""
echo "Removed worktree : $TARGET"
echo "Deleted branch   : $BRANCH"
