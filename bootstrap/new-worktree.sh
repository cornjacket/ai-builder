#!/usr/bin/env bash
# Create a new git worktree for a branch.
#
# Must be run from the main worktree. Fetches remote state before acting.
#
# Usage:
#   new-worktree.sh <branch-name> [--from <base-branch>]
#
# Options:
#   --from <base-branch>   branch to create from (default: main)
#
# Examples:
#   new-worktree.sh feat-x
#   new-worktree.sh experiment --from main

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Script lives in <worktree>/bootstrap/ — workspace is two levels up
WORKSPACE="$(cd "$SCRIPT_DIR/../.." && pwd)"

BRANCH=""
BASE="main"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --from) BASE="$2"; shift 2 ;;
        -*) echo "Unknown flag: $1"; exit 1 ;;
        *) BRANCH="$1"; shift ;;
    esac
done

if [[ -z "$BRANCH" ]]; then
    echo "Usage: new-worktree.sh <branch-name> [--from <base-branch>]"
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
# Fetch remote state
# ---------------------------------------------------------------------------

echo "Fetching remote state..."
git -C "$WORKSPACE/main" fetch --prune origin

# ---------------------------------------------------------------------------
# Create worktree
# ---------------------------------------------------------------------------

TARGET="$WORKSPACE/$BRANCH"

if [[ -e "$TARGET" ]]; then
    echo "ERROR: $TARGET already exists."
    exit 1
fi

echo "Creating worktree '$BRANCH' (from '$BASE')..."
git -C "$WORKSPACE/main" worktree add "$TARGET" -b "$BRANCH" "$BASE"

echo ""
echo "Worktree ready: $TARGET"
echo "Branch: $BRANCH"
