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
TARGET="$REPO_ROOT/sandbox/regressions/template-setup/target"
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
# 2b. --upgrade refreshes machinery without touching content
#
# The generator overwrites machinery unconditionally but only seeds
# user-editable files when absent, so an upgrade must repair a drifted script
# while leaving task content, a hand-edited seeded file, and hand-written
# CLAUDE.md prose alone.
# ---------------------------------------------------------------------------

echo ""
echo "--- 2b. setup-project.sh --upgrade ---"

echo "# DRIFTED" >> "$TARGET/project/tasks/scripts/list-tasks.sh"
echo "MY STATUS NOTES" >> "$TARGET/project/status/README.md"
printf '\n## My own section\nhand written\n' >> "$TARGET/CLAUDE.md"

bash "$REPO_ROOT/target/setup-project.sh" "$TARGET" --upgrade > /dev/null

check_not_contains "$TARGET/project/tasks/scripts/list-tasks.sh" "DRIFTED" \
    "upgrade repairs a drifted machinery script"
check_contains "$TARGET/project/status/README.md" "MY STATUS NOTES" \
    "upgrade preserves a hand-edited seeded file"
check_contains "$TARGET/CLAUDE.md" "My own section" \
    "upgrade preserves hand-written CLAUDE.md prose"

BLOCK_COUNT=$(grep -c "task-system:begin" "$TARGET/CLAUDE.md")
[[ "$BLOCK_COUNT" -eq 1 ]] \
    && pass "upgrade does not duplicate the task-system block (count: $BLOCK_COUNT)" \
    || fail "upgrade duplicated the task-system block (count: $BLOCK_COUNT)"

# --upgrade on a real directory that was never installed into must be rejected,
# not silently treated as a fresh install.
BARE_DIR="$TARGET/../bare-uninstalled"
rm -rf "$BARE_DIR"; mkdir -p "$BARE_DIR"
OUTPUT=$(bash "$REPO_ROOT/target/setup-project.sh" "$BARE_DIR" --upgrade 2>&1 || true)
echo "$OUTPUT" | grep -q "no existing installation" \
    && pass "--upgrade on a never-installed target is rejected" \
    || fail "--upgrade on a never-installed target was not rejected"
[[ ! -d "$BARE_DIR/project/tasks" ]] \
    && pass "rejected --upgrade installed nothing" \
    || fail "rejected --upgrade installed anyway"
rm -rf "$BARE_DIR"

# ---------------------------------------------------------------------------
# 3. setup-project.sh produced CLAUDE.md and the GEMINI.md symlink
#
# There is no init-claude-md.sh step any more: the pinned task-system
# generator injects the CLAUDE.md block during setup, and setup-project.sh
# adds the GEMINI.md symlink as a repo convention.
# ---------------------------------------------------------------------------

echo ""
echo "--- 3. CLAUDE.md / GEMINI.md ---"

[[ -f "$TARGET/CLAUDE.md" ]] \
    && pass "CLAUDE.md created" \
    || fail "CLAUDE.md missing"

check_contains "$TARGET/CLAUDE.md" "task-system:begin" "CLAUDE.md contains the task-system block"

[[ -L "$TARGET/GEMINI.md" ]] \
    && pass "GEMINI.md is a symlink" \
    || fail "GEMINI.md is not a symlink"

LINK_TARGET=$(readlink "$TARGET/GEMINI.md" 2>/dev/null || echo "")
[[ "$LINK_TARGET" == "CLAUDE.md" ]] \
    && pass "GEMINI.md -> CLAUDE.md" \
    || fail "GEMINI.md points to '$LINK_TARGET' instead of CLAUDE.md"

# ---------------------------------------------------------------------------
# 4. The task-system block is not duplicated
# ---------------------------------------------------------------------------

echo ""
echo "--- 4. CLAUDE.md block not duplicated ---"

SECTION_COUNT=$(grep -c "task-system:begin" "$TARGET/CLAUDE.md")
[[ "$SECTION_COUNT" -eq 1 ]] \
    && pass "task-system block not duplicated (count: $SECTION_COUNT)" \
    || fail "task-system block duplicated (count: $SECTION_COUNT)"

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

OUTPUT=$(project/tasks/scripts/new-user-task.sh --epic "$EPIC" --folder draft --name my-test-task --priority HIGH 2>&1)
TASK_DIR=$(echo "$OUTPUT" | grep "Created user-task:" | sed 's/.*Created user-task: *//' | sed 's|/$||')
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

OUTPUT=$(project/tasks/scripts/new-user-subtask.sh --epic "$EPIC" --folder draft --parent "$TASK_NAME" --name my-subtask 2>&1)
SUBTASK_DIR=$(echo "$OUTPUT" | grep "Created user-subtask:" | sed 's/.*Created user-subtask: *//' | sed 's|/$||')
SUBTASK_NAME=$(basename "$SUBTASK_DIR")

check_dir  "$TARGET/$SUBTASK_DIR"
check_contains "$TARGET/$SUBTASK_DIR/README.md" "my-subtask"  "subtask README contains subtask name"
check_contains "$TARGET/$SUBTASK_DIR/README.md" "| Status"    "subtask README has Status field"
check_contains "$TARGET/$SUBTASK_DIR/README.md" "—"           "subtask README Status is —"
check_contains "$TARGET/$TASK_DIR/README.md" "$SUBTASK_NAME"   "subtask listed in parent README"

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
check_contains "$TARGET/project/tasks/$EPIC/in-progress/$TASK_NAME/X-$SUBTASK_NAME/README.md" "complete" "subtask Status updated to complete"

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
