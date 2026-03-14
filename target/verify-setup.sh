#!/usr/bin/env bash
# Verify that the ai-builder project management system is correctly installed
# in a target repository. Read-only — does not modify the target.
#
# Usage:
#   target/verify-setup.sh <target-path> [--epic <epic>]
#
# Exit codes:
#   0 — all checks passed
#   1 — one or more checks failed

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <target-path> [--epic <epic>]" >&2
    exit 1
fi

TARGET="$1"
shift

EPIC="main"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --epic) EPIC="$2"; shift 2 ;;
        *) echo "Unknown argument: $1" >&2; exit 1 ;;
    esac
done

PASS=0
FAIL=0

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

check_dir()  { [[ -d "$1" ]]  && pass "$1 exists"         || fail "$1 missing"; }
check_file() { [[ -f "$1" ]]  && pass "$1 exists"         || fail "$1 missing"; }
check_link() { [[ -L "$1" ]]  && pass "$1 is a symlink"   || fail "$1 is not a symlink"; }
check_exec() { [[ -x "$1" ]]  && pass "$1 is executable"  || fail "$1 not executable"; }

check_contains() {
    local file="$1" pattern="$2" label="$3"
    grep -q "$pattern" "$file" \
        && pass "$label" \
        || fail "$label (pattern '$pattern' not found in $file)"
}

# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

echo "=== verify-setup: $TARGET (epic: $EPIC) ==="
echo ""

echo "--- directories ---"
check_dir "$TARGET/project/tasks/scripts"
check_dir "$TARGET/project/tasks/$EPIC/inbox"
check_dir "$TARGET/project/tasks/$EPIC/draft"
check_dir "$TARGET/project/tasks/$EPIC/backlog"
check_dir "$TARGET/project/tasks/$EPIC/in-progress"
check_dir "$TARGET/project/tasks/$EPIC/complete"
check_dir "$TARGET/project/tasks/$EPIC/wont-do"
check_dir "$TARGET/project/status"

echo ""
echo "--- scripts ---"
check_file "$TARGET/project/tasks/README.md"
check_file "$TARGET/project/tasks/scripts/new-task.sh"
check_file "$TARGET/project/tasks/scripts/move-task.sh"
check_file "$TARGET/project/tasks/scripts/complete-task.sh"
check_file "$TARGET/project/tasks/scripts/list-tasks.sh"
check_file "$TARGET/project/tasks/scripts/show-task.sh"
check_file "$TARGET/project/tasks/scripts/delete-task.sh"
check_file "$TARGET/project/tasks/scripts/restore-task.sh"
check_file "$TARGET/project/tasks/scripts/wont-do-subtask.sh"
check_exec "$TARGET/project/tasks/scripts/new-task.sh"
check_exec "$TARGET/project/tasks/scripts/complete-task.sh"
check_exec "$TARGET/project/tasks/scripts/move-task.sh"
check_exec "$TARGET/project/tasks/scripts/list-tasks.sh"

echo ""
echo "--- templates ---"
check_file "$TARGET/project/tasks/scripts/task-template.md"

echo ""
echo "--- CLAUDE.md / GEMINI.md ---"
check_file "$TARGET/CLAUDE.md"
check_link "$TARGET/GEMINI.md"
check_contains "$TARGET/CLAUDE.md" "task-management-start" "CLAUDE.md contains task management section"
check_contains "$TARGET/CLAUDE.md" "new-task.sh"           "CLAUDE.md contains scripts reference"

LINK_TARGET=$(readlink "$TARGET/GEMINI.md")
[[ "$LINK_TARGET" == "CLAUDE.md" ]] \
    && pass "GEMINI.md -> CLAUDE.md" \
    || fail "GEMINI.md points to '$LINK_TARGET' instead of CLAUDE.md"

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

echo ""
echo "======================================="
echo "Results: $PASS passed, $FAIL failed"
echo "======================================="

[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
