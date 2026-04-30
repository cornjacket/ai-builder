#!/usr/bin/env bash
# Create a new top-level user-task directory with a user-task-template README.md.
# Updates the status folder's README.md task list.
#
# Usage:
#   new-user-task.sh --epic <epic> --folder <status> --name <task-name> --category <name> [--id HEX] [--tags <tags>] [--priority <p>]
#
# --category NAME  Required. The worktree class this task belongs to. Must be a
#                  branch name from project/tasks/classes.md, or the literal
#                  `unclassified` if no class fits. Run with an unknown value to
#                  see the list of valid options. The CLAUDE.md rule requires
#                  every USER-TASK to have a non-empty Category — this flag
#                  enforces it at creation time.
#
# --id HEX  Use the given 6-char hex string as the task ID instead of generating
#           a random one. Intended for replay regression tests that need to
#           reproduce the exact task directory names from a prior recording.
#
# Priority values: CRITICAL, HIGH, MED, LOW (default: —)
#
# Examples:
#   new-user-task.sh --epic main --folder draft --name my-feature --category task-tooling
#   new-user-task.sh --epic main --folder in-progress --name my-feature --category docs --priority HIGH
#   new-user-task.sh --epic main --folder in-progress --name my-feature --category unclassified --id 61857e

set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPTS_DIR/../../.." && pwd)"
# shellcheck source=task-id-helpers.sh
source "$SCRIPTS_DIR/task-id-helpers.sh"
TASK_TEMPLATE="$SCRIPTS_DIR/user-task-template.md"

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------

EPIC="main"
FOLDER=""
NAME=""
TAGS="—"
PRIORITY="—"
CATEGORY=""
FIXED_ID=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --epic)     EPIC="$2";     shift 2 ;;
        --folder)   FOLDER="$2";   shift 2 ;;
        --name)     NAME="$2";     shift 2 ;;
        --id)       FIXED_ID="$2"; shift 2 ;;
        --tags)     TAGS="$2";     shift 2 ;;
        --priority) PRIORITY="$2"; shift 2 ;;
        --category) CATEGORY="$2"; shift 2 ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
done

if [[ -z "$FOLDER" || -z "$NAME" || -z "$CATEGORY" ]]; then
    echo "Usage: new-user-task.sh --folder <status> --name <task-name> --category <name> [--epic <epic>] [--id HEX] [--tags <tags>] [--priority <CRITICAL|HIGH|MED|LOW>]"
    exit 1
fi

# ---------------------------------------------------------------------------
# Validate --category against worktree branches in project/tasks/classes.md
# ---------------------------------------------------------------------------

CLASSES_FILE="$REPO_ROOT/project/tasks/classes.md"
if [[ ! -f "$CLASSES_FILE" ]]; then
    echo "Error: $CLASSES_FILE not found — cannot validate --category." >&2
    exit 1
fi

# Extract branch names from `**Worktree branch:** \`name\`` lines.
VALID_CATEGORIES="$(grep -oE '^\*\*Worktree branch:\*\* `[^`]+`' "$CLASSES_FILE" \
    | sed 's/^\*\*Worktree branch:\*\* `\([^`]*\)`/\1/')"

if [[ -z "$VALID_CATEGORIES" ]]; then
    echo "Error: no worktree branches found in $CLASSES_FILE." >&2
    exit 1
fi

# `unclassified` is always permitted (per CLAUDE.md rule for tasks that fit no class).
if [[ "$CATEGORY" != "unclassified" ]] \
   && ! grep -qxF "$CATEGORY" <<< "$VALID_CATEGORIES"; then
    {
        echo "Error: unknown --category value: '$CATEGORY'"
        echo "Valid values (from $CLASSES_FILE):"
        sed 's/^/  /' <<< "$VALID_CATEGORIES"
        echo "  unclassified"
    } >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------

STATUS_DIR="$REPO_ROOT/project/tasks/$EPIC/$FOLDER"

if [[ ! -d "$STATUS_DIR" ]]; then
    echo "Status directory not found: $STATUS_DIR"
    exit 1
fi

STATUS="$FOLDER"
CREATED="$(date +%Y-%m-%d)"

# Generate a short unique ID and build the directory name
if [[ -n "$FIXED_ID" ]]; then
    ID="$FIXED_ID"
else
    ID="$(openssl rand -hex 3)"
fi
DIRNAME="$ID-$NAME"

TASK_DIR="$STATUS_DIR/$DIRNAME"
PARENT_README="$STATUS_DIR/README.md"

# ---------------------------------------------------------------------------
# Create task directory and README
# ---------------------------------------------------------------------------

mkdir -p "$TASK_DIR"

sed \
    -e "s/{{NAME}}/$NAME/g" \
    -e "s/{{STATUS}}/$STATUS/g" \
    -e "s/{{EPIC}}/$EPIC/g" \
    -e "s/{{TAGS}}/$TAGS/g" \
    -e "s/{{PRIORITY}}/$PRIORITY/g" \
    -e "s/{{CATEGORY}}/$CATEGORY/g" \
    -e "s/{{CREATED}}/$CREATED/g" \
    "$TASK_TEMPLATE" > "$TASK_DIR/README.md"

# ---------------------------------------------------------------------------
# Create parent README if it doesn't exist (status directory case)
# ---------------------------------------------------------------------------

if [[ ! -f "$PARENT_README" ]]; then
    cat > "$PARENT_README" << EOF
# $EPIC / $FOLDER

## Tasks

<!-- When a task is finished, run move-task.sh --to complete before moving on. -->
<!-- task-list-start -->
<!-- task-list-end -->
EOF
fi

# ---------------------------------------------------------------------------
# Append to parent README
# ---------------------------------------------------------------------------

if grep -q "<!-- task-list-end -->" "$PARENT_README"; then
    _sed_i "s|<!-- task-list-end -->|- [$DIRNAME]($DIRNAME/)\n<!-- task-list-end -->|" "$PARENT_README"
else
    echo "Warning: no task list markers found in $PARENT_README — add the entry manually."
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

echo "Created user-task: project/tasks/$EPIC/$FOLDER/$DIRNAME/"
echo "Updated:           $PARENT_README"
