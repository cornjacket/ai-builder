#!/usr/bin/env bash
# Create a new git worktree for a branch.
# Run from inside any existing worktree (e.g., main/).
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
