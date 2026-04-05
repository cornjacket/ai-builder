#!/usr/bin/env bash
# Remove a git worktree and optionally clean up its branch.
#
# What this script does:
#   1. Verifies the branch has no unpushed commits — aborts if local commits
#      exist that are not on the remote, preventing accidental data loss.
#      Pass --skip-push-check to bypass this guard (e.g. for branches that
#      were never intended to be pushed).
#   2. Removes the worktree directory (git worktree remove).
#   3. If --delete-branch is passed:
#        a. Deletes the local branch (safe delete — refuses if unmerged into
#           the current HEAD).
#        b. Deletes the remote branch on origin, if one exists.
#
# Run from inside any existing worktree (e.g., main/).
#
# Usage:
#   remove-worktree.sh <branch-name> [--delete-branch] [--skip-push-check]
#
# Options:
#   --delete-branch     Delete the local branch and its remote counterpart
#                       after removing the worktree. Safe-delete only —
#                       refuses if the branch is not fully merged.
#   --skip-push-check   Skip the unpushed-commits guard. Use when the branch
#                       was never pushed (e.g. local-only experiments).
#
# Examples:
#   remove-worktree.sh feat-x
#   remove-worktree.sh feat-x --delete-branch
#   remove-worktree.sh feat-x --delete-branch --skip-push-check

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/../.." && pwd)"

BRANCH=""
DELETE_BRANCH=false
SKIP_PUSH_CHECK=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --delete-branch)    DELETE_BRANCH=true;    shift ;;
        --skip-push-check)  SKIP_PUSH_CHECK=true;  shift ;;
        -*) echo "Unknown flag: $1"; exit 1 ;;
        *)  BRANCH="$1"; shift ;;
    esac
done

if [[ -z "$BRANCH" ]]; then
    echo "Usage: remove-worktree.sh <branch-name> [--delete-branch] [--skip-push-check]"
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

# ---------------------------------------------------------------------------
# Guard: abort if the branch has unpushed commits
# ---------------------------------------------------------------------------

if [[ "$SKIP_PUSH_CHECK" == false ]]; then
    GIT="git -C $WORKSPACE/main"

    # Check whether a remote tracking branch exists at all
    if $GIT rev-parse --verify "origin/$BRANCH" &>/dev/null; then
        UNPUSHED=$($GIT log "origin/$BRANCH..$BRANCH" --oneline 2>/dev/null | wc -l | tr -d ' ')
        if [[ "$UNPUSHED" -gt 0 ]]; then
            echo "ERROR: branch '$BRANCH' has $UNPUSHED unpushed commit(s):"
            $GIT log "origin/$BRANCH..$BRANCH" --oneline
            echo ""
            echo "Push the branch (or open a PR) before removing the worktree."
            echo "To bypass this check: add --skip-push-check"
            exit 1
        fi
    else
        echo "WARNING: branch '$BRANCH' has no remote tracking ref — it has never been pushed."
        echo "If this is intentional, re-run with --skip-push-check."
        exit 1
    fi
fi

# ---------------------------------------------------------------------------
# Remove worktree
# ---------------------------------------------------------------------------

echo "Removing worktree '$BRANCH'..."
git -C "$WORKSPACE/main" worktree remove "$TARGET"

# ---------------------------------------------------------------------------
# Optionally delete local and remote branch
# ---------------------------------------------------------------------------

if [[ "$DELETE_BRANCH" == true ]]; then
    echo "Deleting local branch '$BRANCH'..."
    git -C "$WORKSPACE/main" branch -d "$BRANCH"

    if git -C "$WORKSPACE/main" ls-remote --exit-code origin "$BRANCH" &>/dev/null; then
        echo "Deleting remote branch 'origin/$BRANCH'..."
        git -C "$WORKSPACE/main" push origin --delete "$BRANCH"
    else
        echo "No remote branch to delete."
    fi
fi

echo ""
echo "Removed worktree: $TARGET"
