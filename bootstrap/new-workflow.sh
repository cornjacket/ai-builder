#!/usr/bin/env bash
# Start a new feature workflow: move task to in-progress, commit, create worktree.
#
# Must be run from the main worktree. Fetches remote state before acting.
#
# Usage:
#   new-workflow.sh -taskname <task-name> -name <worktree-name> [-epic <epic>]
#
# Arguments:
#   -taskname   fully-qualified task name (e.g. f5f7b8-pipeline-acceptance-spec-writer)
#   -name       worktree and branch name (e.g. acceptance-spec)
#   -epic       epic name (default: main)
#
# What this does:
#   1. Verifies it is running from the main worktree and fetches remote state
#   2. Locates the task in draft, backlog, or in-progress
#   3. Moves it to in-progress (if not already there) and commits
#   4. Creates a new worktree branched from the current HEAD
#   5. Prints next steps

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKSPACE="$(cd "$REPO_ROOT/.." && pwd)"

TASK_NAME=""
WORKTREE_NAME=""
EPIC="main"

while [[ $# -gt 0 ]]; do
    case "$1" in
        -taskname|--taskname|-task-name|--task-name)
            TASK_NAME="$2"; shift 2 ;;
        -name|--name)
            WORKTREE_NAME="$2"; shift 2 ;;
        -epic|--epic)
            EPIC="$2"; shift 2 ;;
        *)
            echo "Unknown argument: $1" >&2
            echo "Usage: $0 -taskname <task-name> -name <worktree-name> [-epic <epic>]" >&2
            exit 1 ;;
    esac
done

if [[ -z "$TASK_NAME" || -z "$WORKTREE_NAME" ]]; then
    echo "Usage: $0 -taskname <task-name> -name <worktree-name> [-epic <epic>]" >&2
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
# Locate the task
# ---------------------------------------------------------------------------

TASKS_ROOT="$REPO_ROOT/project/tasks/$EPIC"
CURRENT_FOLDER=""
for folder in draft backlog in-progress; do
    if [[ -d "$TASKS_ROOT/$folder/$TASK_NAME" ]]; then
        CURRENT_FOLDER="$folder"
        break
    fi
done

if [[ -z "$CURRENT_FOLDER" ]]; then
    echo "ERROR: Task '$TASK_NAME' not found in draft, backlog, or in-progress (epic: $EPIC)" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Move to in-progress and commit (skip if already there)
# ---------------------------------------------------------------------------

if [[ "$CURRENT_FOLDER" != "in-progress" ]]; then
    echo ""
    echo "=== Moving $TASK_NAME to in-progress ==="
    bash "$REPO_ROOT/project/tasks/scripts/move-task.sh" \
        --epic "$EPIC" \
        --name "$TASK_NAME" \
        --from "$CURRENT_FOLDER" \
        --to   in-progress

    echo ""
    echo "=== Committing task move ==="
    git -C "$REPO_ROOT" add project/tasks/
    git -C "$REPO_ROOT" commit -m "Move $TASK_NAME to in-progress

Task: $TASK_NAME"
    echo ""
else
    echo "Task '$TASK_NAME' is already in in-progress — skipping move."
    echo ""
fi

# ---------------------------------------------------------------------------
# Create the worktree (branches from current HEAD, which has the move)
# ---------------------------------------------------------------------------

echo "=== Creating worktree '$WORKTREE_NAME' ==="
bash "$SCRIPT_DIR/new-worktree.sh" "$WORKTREE_NAME"

# ---------------------------------------------------------------------------
# Next steps
# ---------------------------------------------------------------------------

echo ""
echo "================================================================"
echo " Workflow ready"
echo "================================================================"
echo ""
echo "  Task     : $TASK_NAME (in-progress)"
echo "  Worktree : $WORKSPACE/$WORKTREE_NAME"
echo "  Branch   : $WORKTREE_NAME"
echo ""
echo "Next steps:"
echo "  1. Open a new session pointed at: $WORKSPACE/$WORKTREE_NAME"
echo "  2. Implement $TASK_NAME in that worktree"
echo "  3. When done, open a PR and merge to main"
echo "  4. Remove the worktree (after merge):"
echo "       bash bootstrap/remove-worktree.sh $WORKTREE_NAME"
echo ""
