#!/usr/bin/env bash
# List all projects under project/projects/ with their builds and status.
#
# Usage:
#   list-projects.sh

set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPTS_DIR/../../.." && pwd)"
PROJECTS_DIR="$REPO_ROOT/project/projects"

if [[ ! -d "$PROJECTS_DIR" ]]; then
    echo "No projects directory found at project/projects/"
    exit 0
fi

# ---------------------------------------------------------------------------
# List projects and builds
# ---------------------------------------------------------------------------

found=0

for PROJECT_DIR in "$PROJECTS_DIR"/*/; do
    [[ -d "$PROJECT_DIR" ]] || continue
    PROJECT_NAME="$(basename "$PROJECT_DIR")"

    # Skip hidden directories
    [[ "$PROJECT_NAME" == .* ]] && continue

    found=1
    echo "$PROJECT_NAME"

    # List build-N subdirectories
    for BUILD_DIR in "$PROJECT_DIR"*/; do
        [[ -d "$BUILD_DIR" ]] || continue
        BUILD_NAME="$(basename "$BUILD_DIR")"

        # Skip hidden directories and the main epic directory
        [[ "$BUILD_NAME" == .* ]] && continue
        [[ "$BUILD_NAME" == "main" ]] && continue

        # Read status from README
        BUILD_README="$BUILD_DIR/README.md"
        STATUS="—"
        if [[ -f "$BUILD_README" ]]; then
            STATUS=$(grep "^| Status" "$BUILD_README" | head -1 | sed 's/| Status *| *\([^|]*\) *|.*/\1/' | xargs)
        fi

        echo "  └── $BUILD_NAME [$STATUS]"
    done
done

if [[ $found -eq 0 ]]; then
    echo "No projects found."
fi
