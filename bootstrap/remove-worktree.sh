#!/usr/bin/env bash
# Remove a git worktree.
# Run from inside any existing worktree (e.g., main/).
#
# Usage:
#   remove-worktree.sh <branch-name> [--delete-branch]
#
# Options:
#   --delete-branch   also delete the branch (safe delete — refuses if unmerged)
#
# Examples:
#   remove-worktree.sh feat-x
#   remove-worktree.sh feat-x --delete-branch

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/../.." && pwd)"

BRANCH=""
DELETE_BRANCH=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --delete-branch) DELETE_BRANCH=true; shift ;;
        -*) echo "Unknown flag: $1"; exit 1 ;;
        *) BRANCH="$1"; shift ;;
    esac
done

if [[ -z "$BRANCH" ]]; then
    echo "Usage: remove-worktree.sh <branch-name> [--delete-branch]"
    exit 1
fi

if [[ "$BRANCH" == "main" ]]; then
    echo "ERROR: cannot remove the main worktree."
    exit 1
fi

TARGET="$WORKSPACE/$BRANCH"

if [[ ! -d "$TARGET" ]]; then
    echo "ERROR: worktree not found: $TARGET"
    exit 1
fi

echo "Removing worktree '$BRANCH'..."
git -C "$WORKSPACE/main" worktree remove "$TARGET"

if [[ "$DELETE_BRANCH" == true ]]; then
    echo "Deleting branch '$BRANCH'..."
    git -C "$WORKSPACE/main" branch -d "$BRANCH"
fi

echo ""
echo "Removed worktree: $TARGET"
