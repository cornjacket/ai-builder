#!/usr/bin/env bash
# End-to-end regression test for the ai-builder project management template.
# Run from the repo root:
#   tests/regression/template-setup/test.sh
#
# Exit codes:
#   0 — all checks passed
#   1 — one or more checks failed

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
TARGET=/tmp/ai-builder-target
EPIC="main"

PASS=0
FAIL=0

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

check_dir()  { [[ -d "$1" ]]  && pass "$1 exists"          || fail "$1 missing"; }

check_contains() {
    local file="$1" pattern="$2" label="$3"
    grep -q "$pattern" "$file" \
        && pass "$label" \
        || fail "$label (pattern '$pattern' not found in $file)"
}

check_not_contains() {
    local file="$1" pattern="$2" label="$3"
    ! grep -q "$pattern" "$file" \
        && pass "$label" \
        || fail "$label (pattern '$pattern' unexpectedly found in $file)"
}

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

echo "=== Template Setup Regression Test ==="
echo "    repo root: $REPO_ROOT"
echo "    target:    $TARGET"
echo ""

# Fresh start
rm -rf "$TARGET"
mkdir -p "$TARGET"

# ---------------------------------------------------------------------------
# 1. setup-project.sh installs correct structure
# ---------------------------------------------------------------------------

echo "--- 1. setup-project.sh ---"

bash "$REPO_ROOT/target/setup-project.sh" "$TARGET" --epic "$EPIC" > /dev/null

# ---------------------------------------------------------------------------
# 2. setup-project.sh is idempotent
# ---------------------------------------------------------------------------

echo ""
echo "--- 2. setup-project.sh idempotency ---"

OUTPUT=$(bash "$REPO_ROOT/target/setup-project.sh" "$TARGET" 2>&1)
echo "$OUTPUT" | grep -q "already installed" \
    && pass "second run detects existing installation" \
    || fail "second run did not detect existing installation"

# ---------------------------------------------------------------------------
# 3. init-claude-md.sh creates CLAUDE.md and GEMINI.md
# ---------------------------------------------------------------------------

echo ""
echo "--- 3. init-claude-md.sh ---"

bash "$REPO_ROOT/target/init-claude-md.sh" "$TARGET" > /dev/null

# ---------------------------------------------------------------------------
# 4. init-claude-md.sh is idempotent
# ---------------------------------------------------------------------------

echo ""
echo "--- 4. init-claude-md.sh idempotency ---"

OUTPUT=$(bash "$REPO_ROOT/target/init-claude-md.sh" "$TARGET" 2>&1)
echo "$OUTPUT" | grep -q "already present" \
    && pass "second run detects existing task management section" \
    || fail "second run did not detect existing task management section"

SECTION_COUNT=$(grep -c "task-management-start" "$TARGET/CLAUDE.md")
[[ "$SECTION_COUNT" -eq 1 ]] \
    && pass "task management section not duplicated (count: $SECTION_COUNT)" \
    || fail "task management section duplicated (count: $SECTION_COUNT)"

# ---------------------------------------------------------------------------
# 5. verify-setup.sh passes
# ---------------------------------------------------------------------------

echo ""
echo "--- 5. verify-setup.sh ---"

"$REPO_ROOT/target/verify-setup.sh" "$TARGET" --epic "$EPIC"
VERIFY_EXIT=$?
[[ "$VERIFY_EXIT" -eq 0 ]] \
    && pass "verify-setup.sh passed" \
    || fail "verify-setup.sh failed (exit $VERIFY_EXIT)"

# ---------------------------------------------------------------------------
# 6. new-task.sh creates a task
# ---------------------------------------------------------------------------

echo ""
echo "--- 6. new-task.sh (task) ---"

cd "$TARGET"

OUTPUT=$(project/tasks/scripts/new-task.sh --epic "$EPIC" --folder draft --name my-test-task --priority HIGH 2>&1)
TASK_DIR=$(echo "$OUTPUT" | grep "Created task:" | sed 's/.*Created task: *//' | sed 's|/$||')
TASK_NAME=$(basename "$TASK_DIR")

check_dir  "$TARGET/$TASK_DIR"
check_contains "$TARGET/$TASK_DIR/README.md" "my-test-task"  "task README contains task name"
check_contains "$TARGET/$TASK_DIR/README.md" "| Status"      "task README has Status field"
check_contains "$TARGET/$TASK_DIR/README.md" "draft"         "task README Status is draft"
check_contains "$TARGET/project/tasks/$EPIC/draft/README.md" "$TASK_NAME" "task listed in draft README"

# ---------------------------------------------------------------------------
# 7. new-task.sh creates a subtask
# ---------------------------------------------------------------------------

echo ""
echo "--- 7. new-task.sh (subtask) ---"

OUTPUT=$(project/tasks/scripts/new-task.sh --epic "$EPIC" --folder draft --parent "$TASK_NAME" --name my-subtask 2>&1)
SUBTASK_DIR=$(echo "$OUTPUT" | grep "Created subtask:" | sed 's/.*Created subtask: *//' | sed 's|/$||')
SUBTASK_NAME=$(basename "$SUBTASK_DIR")

check_dir  "$TARGET/$SUBTASK_DIR"
check_contains "$TARGET/$SUBTASK_DIR/README.md" "my-subtask"  "subtask README contains subtask name"
check_contains "$TARGET/$SUBTASK_DIR/README.md" "| Status"    "subtask README has Status field"
check_contains "$TARGET/$SUBTASK_DIR/README.md" "—"           "subtask README Status is —"
check_contains "$TARGET/$TASK_DIR/README.md" "$SUBTASK_NAME"  "subtask listed in parent README"

# ---------------------------------------------------------------------------
# 8. move-task.sh moves task to backlog
# ---------------------------------------------------------------------------

echo ""
echo "--- 8. move-task.sh (draft -> backlog) ---"

project/tasks/scripts/move-task.sh --epic "$EPIC" --name "$TASK_NAME" --from draft --to backlog > /dev/null

check_dir  "$TARGET/project/tasks/$EPIC/backlog/$TASK_NAME"
check_not_contains "$TARGET/project/tasks/$EPIC/draft/README.md"   "$TASK_NAME" "task removed from draft README"
check_contains     "$TARGET/project/tasks/$EPIC/backlog/README.md" "$TASK_NAME" "task added to backlog README"
check_contains     "$TARGET/project/tasks/$EPIC/backlog/$TASK_NAME/README.md" "backlog" "task Status updated to backlog"

# ---------------------------------------------------------------------------
# 9. move-task.sh moves task to in-progress
# ---------------------------------------------------------------------------

echo ""
echo "--- 9. move-task.sh (backlog -> in-progress) ---"

project/tasks/scripts/move-task.sh --epic "$EPIC" --name "$TASK_NAME" --from backlog --to in-progress > /dev/null

check_dir "$TARGET/project/tasks/$EPIC/in-progress/$TASK_NAME"
check_contains "$TARGET/project/tasks/$EPIC/in-progress/$TASK_NAME/README.md" "in-progress" "task Status updated to in-progress"

# ---------------------------------------------------------------------------
# 10. list-tasks.sh shows correct output
# ---------------------------------------------------------------------------

echo ""
echo "--- 10. list-tasks.sh ---"

OUTPUT=$(project/tasks/scripts/list-tasks.sh --epic "$EPIC" --folder in-progress --depth 2 2>&1)
echo "$OUTPUT" | grep -q "$TASK_NAME" \
    && pass "list-tasks.sh shows task in in-progress" \
    || fail "list-tasks.sh did not show task in in-progress"

echo "$OUTPUT" | grep -q "$SUBTASK_NAME" \
    && pass "list-tasks.sh shows subtask at depth 2" \
    || fail "list-tasks.sh did not show subtask at depth 2"

# ---------------------------------------------------------------------------
# 11. complete-task.sh --parent marks subtask complete
# ---------------------------------------------------------------------------

echo ""
echo "--- 11. complete-task.sh (subtask) ---"

project/tasks/scripts/complete-task.sh --epic "$EPIC" --folder in-progress --parent "$TASK_NAME" --name "$SUBTASK_NAME" > /dev/null

check_contains "$TARGET/project/tasks/$EPIC/in-progress/$TASK_NAME/README.md" "\[x\].*$SUBTASK_NAME" "subtask marked [x] in parent README"
check_contains "$TARGET/project/tasks/$EPIC/in-progress/$TASK_NAME/$SUBTASK_NAME/README.md" "complete" "subtask Status updated to complete"

# ---------------------------------------------------------------------------
# 12. complete-task.sh moves top-level task to complete/
# ---------------------------------------------------------------------------

echo ""
echo "--- 12. complete-task.sh (top-level task) ---"

project/tasks/scripts/complete-task.sh --epic "$EPIC" --folder in-progress --name "$TASK_NAME" > /dev/null

check_dir  "$TARGET/project/tasks/$EPIC/complete/$TASK_NAME"
check_not_contains "$TARGET/project/tasks/$EPIC/in-progress/README.md" "$TASK_NAME" "task removed from in-progress README"
check_contains     "$TARGET/project/tasks/$EPIC/complete/README.md"    "$TASK_NAME" "task added to complete README"
check_contains     "$TARGET/project/tasks/$EPIC/complete/$TASK_NAME/README.md" "complete" "task Status updated to complete"

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

echo ""
echo "======================================="
echo "Results: $PASS passed, $FAIL failed"
echo "======================================="

[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
