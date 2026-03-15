#!/usr/bin/env bash
# Create a new project under project/projects/ with a user-task README
# and a default main epic with all status subdirectories.
#
# Usage:
#   new-project.sh --name <project-name>
#
# Examples:
#   new-project.sh --name my-project

set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPTS_DIR/../../.." && pwd)"
TASK_TEMPLATE="$SCRIPTS_DIR/user-task-template.md"

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------

NAME=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --name) NAME="$2"; shift 2 ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
done

if [[ -z "$NAME" ]]; then
    echo "Usage: new-project.sh --name <project-name>"
    exit 1
fi

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------

PROJECTS_DIR="$REPO_ROOT/project/projects"
PROJECT_DIR="$PROJECTS_DIR/$NAME"

if [[ -d "$PROJECT_DIR" ]]; then
    echo "Project already exists: project/projects/$NAME"
    exit 1
fi

# ---------------------------------------------------------------------------
# Create projects/ directory if it doesn't exist
# ---------------------------------------------------------------------------

mkdir -p "$PROJECTS_DIR"

# ---------------------------------------------------------------------------
# Create project directory and user-task README
# ---------------------------------------------------------------------------

mkdir -p "$PROJECT_DIR"

sed \
    -e "s/{{NAME}}/$NAME/g" \
    -e "s/{{STATUS}}/—/g" \
    -e "s/{{EPIC}}/—/g" \
    -e "s/{{TAGS}}/—/g" \
    -e "s/{{PRIORITY}}/—/g" \
    "$TASK_TEMPLATE" > "$PROJECT_DIR/README.md"

echo "Created project: project/projects/$NAME/"

# ---------------------------------------------------------------------------
# Create default main epic with status directories
# ---------------------------------------------------------------------------

"$SCRIPTS_DIR/new-epic.sh" --name main --project "$NAME"
