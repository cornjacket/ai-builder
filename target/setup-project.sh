#!/usr/bin/env bash
# Install the ai-builder project management system into a target repository.
#
# Usage:
#   setup-project.sh <target-repo-path> [--epic <name>]
#
# Options:
#   --epic <name>   Epic name for the initial directory structure (default: main)
#
# Example:
#   setup-project.sh ~/code/my-app
#   setup-project.sh ~/code/my-app --epic core

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/project"

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------

TARGET_REPO=""
EPIC="main"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --epic) EPIC="$2"; shift 2 ;;
        -*) echo "Unknown flag: $1"; exit 1 ;;
        *)
            if [[ -z "$TARGET_REPO" ]]; then
                TARGET_REPO="$1"
            else
                echo "Unexpected argument: $1"
                exit 1
            fi
            shift
            ;;
    esac
done

if [[ -z "$TARGET_REPO" ]]; then
    echo "Usage: setup-project.sh <target-repo-path> [--epic <name>]"
    exit 1
fi

if [[ ! -d "$TARGET_REPO" ]]; then
    echo "Target repository not found: $TARGET_REPO"
    exit 1
fi

TARGET_TASKS="$TARGET_REPO/project/tasks"

# ---------------------------------------------------------------------------
# Idempotency check
# ---------------------------------------------------------------------------

if [[ -d "$TARGET_TASKS" ]]; then
    echo "Project management system already installed at: $TARGET_TASKS"
    echo "Nothing to do. To reinstall, remove $TARGET_TASKS first."
    exit 0
fi

# ---------------------------------------------------------------------------
# Copy template
# ---------------------------------------------------------------------------

cp -r "$TEMPLATE_DIR" "$TARGET_REPO/project"

# Make all scripts executable
find "$TARGET_REPO/project/tasks/scripts" -name "*.sh" -exec chmod +x {} \;

# ---------------------------------------------------------------------------
# Create epic directory structure
# ---------------------------------------------------------------------------

for folder in inbox draft backlog in-progress complete wont-do; do
    mkdir -p "$TARGET_TASKS/$EPIC/$folder"
    # Remove placeholder if it exists (copied from template)
    rm -f "$TARGET_TASKS/$EPIC/$folder/.gitkeep"
    touch "$TARGET_TASKS/$EPIC/$folder/.gitkeep"
done

# Remove the generic placeholder from main/ if a different epic was requested
if [[ "$EPIC" != "main" ]]; then
    for folder in inbox draft backlog in-progress complete wont-do; do
        rm -rf "$TARGET_TASKS/main/$folder"
    done
    rmdir "$TARGET_TASKS/main" 2>/dev/null || true
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

echo "Installed project management system into: $TARGET_REPO/project/"
echo ""
echo "  tasks/scripts/   — management scripts"
echo "  tasks/$EPIC/     — epic directory (inbox, draft, backlog, in-progress, complete, wont-do)"
echo "  status/          — daily status reports"
echo ""
echo "Next steps:"
echo "  1. Run init-claude-md.sh $TARGET_REPO to set up CLAUDE.md"
echo "  2. Read $TARGET_REPO/project/tasks/README.md for usage instructions"
echo "  3. Create your first task:"
echo "     $TARGET_REPO/project/tasks/scripts/new-user-task.sh --epic $EPIC --folder draft --name my-first-task"
