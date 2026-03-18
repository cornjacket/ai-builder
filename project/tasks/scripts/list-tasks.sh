#!/usr/bin/env bash
# List all tasks in an epic, grouped by status.
# Reads task order and completion state from each directory's README.md.
# Optionally filter to a single status folder, set recursion depth, or
# specify a traversal root directly.
#
# By default only incomplete tasks are shown. Use --all to show everything.
# Use --tag to filter to tasks whose Tags field contains the given value.
# Use --sort-priority to sort tasks HIGH → MED → LOW → unset within each folder.
#
# Usage:
#   list-tasks.sh [--epic <epic>] [--folder <status>] [--depth <n>] [--root <path>] [--all] [--tag <tag>] [--sort-priority]
#
# Examples:
#   list-tasks.sh --epic main
#   list-tasks.sh --epic main --all
#   list-tasks.sh --epic main --folder in-progress --depth 2
#   list-tasks.sh --root main/in-progress/my-task --depth 3 --all
#   list-tasks.sh --epic main --tag tooling --depth 2
#   list-tasks.sh --epic main --folder backlog --sort-priority

set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPTS_DIR/../../.." && pwd)"

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------

EPIC="main"
FOLDER=""
DEPTH=1
ROOT=""
SHOW_ALL=false
TAG=""
SORT_PRIORITY=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --epic)            EPIC="$2";   shift 2 ;;
        --folder)          FOLDER="$2"; shift 2 ;;
        --depth)           DEPTH="$2";  shift 2 ;;
        --root)            ROOT="$2";   shift 2 ;;
        --all)             SHOW_ALL=true; shift ;;
        --tag)             TAG="$2";    shift 2 ;;
        --sort-priority)   SORT_PRIORITY=true; shift ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
done

# ---------------------------------------------------------------------------
# Resolve traversal root
# ---------------------------------------------------------------------------

if [[ -n "$ROOT" ]]; then
    ROOT_DIR="$REPO_ROOT/project/tasks/$ROOT"
    if [[ ! -d "$ROOT_DIR" ]]; then
        echo "Root not found: project/tasks/$ROOT"
        exit 1
    fi
else
    EPIC_DIR="$REPO_ROOT/project/tasks/$EPIC"
    if [[ ! -d "$EPIC_DIR" ]]; then
        echo "Epic not found: $EPIC"
        exit 1
    fi
fi

# Status display order
STATUSES=("inbox" "draft" "backlog" "in-progress" "complete" "wont-do")

# ---------------------------------------------------------------------------
# Helper: read Priority field from a task README
# ---------------------------------------------------------------------------

get_priority() {
    local readme="$1"
    local priority
    priority=$(grep -m1 "^| Priority" "$readme" 2>/dev/null | sed 's/| Priority *| *\(.*\) *|/\1/' | tr -d ' ')
    echo "${priority:-—}"
}

# ---------------------------------------------------------------------------
# Helper: map a priority value to a sort key (lower = higher priority)
# ---------------------------------------------------------------------------

priority_sort_key() {
    case "$1" in
        HIGH) echo "1" ;;
        MED)  echo "2" ;;
        LOW)  echo "3" ;;
        *)    echo "4" ;;
    esac
}

# ---------------------------------------------------------------------------
# Helper: check if a task README's Tags field contains the given tag (case-insensitive)
# Returns 0 (true) if tag matches or no TAG filter is set.
# ---------------------------------------------------------------------------

has_tag() {
    local readme="$1"
    [[ -z "$TAG" ]] && return 0
    local tags
    tags=$(grep -m1 "^| Tags" "$readme" 2>/dev/null | sed 's/| Tags *| *\(.*\) *|/\1/' | tr '[:upper:]' '[:lower:]')
    echo "$tags" | grep -qiw "$(echo "$TAG" | tr '[:upper:]' '[:lower:]')"
}

# ---------------------------------------------------------------------------
# Helper: parse task dirnames from a README in listed order.
#
# For task-list entries (no checkbox):   always included.
# For subtask-list entries with [ ]:     always included.
# For subtask-list entries with [x]:     included only when SHOW_ALL=true.
# Falls back to sorted find if no markers are present.
# ---------------------------------------------------------------------------

parse_readme_order() {
    local readme="$1"
    local dir="$2"

    if ! grep -q "<!-- task-list-start -->\|<!-- subtask-list-start -->" "$readme" 2>/dev/null; then
        # No markers — fall back to alphabetical find
        find "$dir" -mindepth 1 -maxdepth 1 -type d -not -name '.*' | sort
        return
    fi

    local in_block=0
    while IFS= read -r line; do
        if [[ "$line" == *"<!-- task-list-start -->"* || "$line" == *"<!-- subtask-list-start -->"* ]]; then
            in_block=1; continue
        fi
        if [[ "$line" == *"<!-- task-list-end -->"* || "$line" == *"<!-- subtask-list-end -->"* ]]; then
            in_block=0; continue
        fi
        [[ $in_block -eq 0 ]] && continue

        # Skip completed subtask entries unless --all
        if [[ "$SHOW_ALL" == false ]] && [[ "$line" == *"- [x]"* ]]; then
            continue
        fi

        # Extract directory name from (dirname/)
        local dirname
        dirname=$(echo "$line" | sed 's/.*(\(.*\)\/)/\1/')
        [[ -z "$dirname" ]] && continue

        local task_dir="$dir/$dirname"
        [[ -d "$task_dir" ]] && echo "$task_dir"
    done < "$readme"
}

# ---------------------------------------------------------------------------
# Recursive print function
# ---------------------------------------------------------------------------

print_dir_tasks() {
    local dir="$1"
    local current_depth="$2"
    local max_depth="$3"
    local indent="$4"
    local readme="$dir/README.md"

    [[ -f "$readme" ]] || return

    while IFS= read -r task_dir; do
        [[ -f "$task_dir/README.md" ]] || continue
        has_tag "$task_dir/README.md" || continue
        local task_name priority
        task_name="$(basename "$task_dir")"
        priority="$(get_priority "$task_dir/README.md")"

        if [[ "$priority" != "—" ]]; then
            echo "${indent}${task_name} [${priority}]"
        else
            echo "${indent}${task_name}"
        fi

        if [[ "$current_depth" -lt "$max_depth" ]]; then
            print_dir_tasks "$task_dir" $(( current_depth + 1 )) "$max_depth" "${indent}  └── "
        fi
    done < <(parse_readme_order "$readme" "$dir")
}

# ---------------------------------------------------------------------------
# Print tasks for a single status folder
# ---------------------------------------------------------------------------

print_status_tasks() {
    local status_dir="$1"
    local status="$2"
    local readme="$status_dir/README.md"
    local has_tasks=0

    # At the status level there are no checkboxes, so we always show all
    # top-level tasks regardless of --all (status folder = completion state).

    # Build the list of task dirs, optionally sorted by priority.
    local task_dirs=()
    while IFS= read -r task_dir; do
        [[ -f "$task_dir/README.md" ]] || continue
        has_tag "$task_dir/README.md" || continue
        task_dirs+=("$task_dir")
    done < <(
        if [[ -f "$readme" ]]; then
            parse_readme_order "$readme" "$status_dir"
        else
            find "$status_dir" -mindepth 1 -maxdepth 1 -type d -not -name '.*' | sort
        fi
    )

    if [[ "$SORT_PRIORITY" == true && ${#task_dirs[@]} -gt 0 ]]; then
        # Decorate with sort key, stable-sort, then undecorate.
        local decorated=()
        for task_dir in "${task_dirs[@]}"; do
            local p key
            p="$(get_priority "$task_dir/README.md")"
            key="$(priority_sort_key "$p")"
            decorated+=("${key}|${task_dir}")
        done
        # Sort by key (first field), preserving original order within same priority.
        local sorted_dirs=()
        while IFS= read -r entry; do
            sorted_dirs+=("${entry#*|}")
        done < <(printf '%s\n' "${decorated[@]}" | sort -t'|' -k1,1 -s)
        task_dirs=("${sorted_dirs[@]}")
    fi

    [[ ${#task_dirs[@]} -eq 0 ]] && return

    for task_dir in "${task_dirs[@]}"; do
        local task_name priority
        task_name="$(basename "$task_dir")"
        priority="$(get_priority "$task_dir/README.md")"

        if [[ $has_tasks -eq 0 ]]; then
            echo ""
            echo "  [$status]"
            has_tasks=1
        fi

        if [[ "$priority" != "—" ]]; then
            echo "    $task_name [$priority]"
        else
            echo "    $task_name"
        fi

        if [[ "$DEPTH" -gt 1 ]]; then
            print_dir_tasks "$task_dir" 2 "$DEPTH" "      └── "
        fi
    done
}

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

FILTER_LABEL="incomplete only"
[[ "$SHOW_ALL" == true ]] && FILTER_LABEL="all"
[[ -n "$TAG" ]] && FILTER_LABEL="$FILTER_LABEL, tag: $TAG"
[[ "$SORT_PRIORITY" == true ]] && FILTER_LABEL="$FILTER_LABEL, sorted by priority"

if [[ -n "$ROOT" ]]; then
    echo "Tasks — root: $ROOT  (depth: $DEPTH, $FILTER_LABEL)"
    echo "========================================"
    echo ""
    print_dir_tasks "$ROOT_DIR" 1 "$DEPTH" "  "
    echo ""
else
    echo "Tasks — epic: $EPIC  (depth: $DEPTH, $FILTER_LABEL)"
    echo "========================================"

    if [[ -n "$FOLDER" ]]; then
        status_dir="$EPIC_DIR/$FOLDER"
        if [[ ! -d "$status_dir" ]]; then
            echo "Status folder not found: $FOLDER"
            exit 1
        fi
        print_status_tasks "$status_dir" "$FOLDER"
    else
        for status in "${STATUSES[@]}"; do
            status_dir="$EPIC_DIR/$status"
            if [[ -d "$status_dir" ]]; then
                print_status_tasks "$status_dir" "$status"
            fi
        done
    fi

    echo ""
fi
