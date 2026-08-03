#!/usr/bin/env bash
# Verify that the ai-builder project management system is correctly installed
# in a target repository. Read-only — does not modify the target.
#
# Checks are grouped by the two layers an installed ai-builder is made of:
#
#   Layer 1 — task system, from the pinned create-project-system generator
#   Layer 2 — pipeline overlay, create-ai-builder's own scripts
#   Conventions — CLAUDE.md / GEMINI.md
#
# The final group is a NEGATIVE check: a target must NOT contain the
# orchestrator, its state machines or its role prompts. The overlay is
# deliberately thin (the orchestrator runs from a create-ai-builder checkout
# and reaches into the target), and copying the engine in would recreate the
# duplicate-copy drift that pinning the generator exists to prevent.
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

TASKS="$TARGET/project/tasks"
SCRIPTS="$TASKS/scripts"

# Layer 2 — create-ai-builder's own pipeline machinery. Kept in step with the
# PIPELINE_SCRIPTS array in setup-project.sh.
PIPELINE_SCRIPTS=(
    advance-pipeline.sh
    check-stop-after.sh
    new-pipeline-build.sh
    new-pipeline-subtask.sh
    on-task-complete.sh
    set-current-job.sh
    pipeline-build-template.md
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

check_dir()     { [[ -d "$1" ]] && pass "$1 exists"        || fail "$1 missing"; }
check_file()    { [[ -f "$1" ]] && pass "$1 exists"        || fail "$1 missing"; }
check_link()    { [[ -L "$1" ]] && pass "$1 is a symlink"  || fail "$1 is not a symlink"; }
check_exec()    { [[ -x "$1" ]] && pass "$1 is executable" || fail "$1 not executable"; }
check_absent()  { [[ ! -e "$1" ]] && pass "$1 absent (as intended)" || fail "$1 present — targets must not carry it"; }

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

echo "--- layer 1: structure ---"
check_dir "$SCRIPTS"
check_dir "$TASKS/docs"
check_dir "$TARGET/project/status"
for folder in inbox draft backlog in-progress complete wont-do; do
    check_dir "$TASKS/$EPIC/$folder"
done

echo ""
echo "--- layer 1: machinery ---"
for f in new-user-task.sh new-user-subtask.sh new-epic.sh move-task.sh \
         complete-task.sh delete-task.sh restore-task.sh wont-do-subtask.sh \
         show-task.sh list-tasks.sh next-subtask.sh is-last-task.sh \
         new-project.sh list-projects.sh; do
    check_file "$SCRIPTS/$f"
done
for f in new-user-task.sh new-user-subtask.sh new-epic.sh move-task.sh \
         complete-task.sh list-tasks.sh new-project.sh list-projects.sh; do
    check_exec "$SCRIPTS/$f"
done

# Decoupled-path config: these are what let the scripts run from a mount other
# than the generator's default.
check_file "$SCRIPTS/task-config.sh"
check_file "$SCRIPTS/task-env.sh"

echo ""
echo "--- layer 1: templates ---"
check_file "$SCRIPTS/user-task-template.md"
check_file "$SCRIPTS/user-subtask-template.md"

echo ""
echo "--- layer 1: docs and skill ---"
check_file "$TASKS/docs/USING.md"
check_file "$TASKS/docs/README.md"
check_file "$TASKS/docs/task-manager.md"
check_file "$TARGET/.claude/skills/task-system/SKILL.md"

echo ""
echo "--- layer 2: pipeline overlay ---"
for f in "${PIPELINE_SCRIPTS[@]}"; do
    check_file "$SCRIPTS/$f"
done
for f in "${PIPELINE_SCRIPTS[@]}"; do
    [[ "$f" == *.sh ]] && check_exec "$SCRIPTS/$f"
done

echo ""
echo "--- layer 2: engine must NOT be installed ---"
check_absent "$TARGET/ai-builder"
check_absent "$TASKS/machines"
check_absent "$TASKS/roles"

echo ""
echo "--- conventions: CLAUDE.md / GEMINI.md ---"
check_file "$TARGET/CLAUDE.md"
check_link "$TARGET/GEMINI.md"
check_contains "$TARGET/CLAUDE.md" "task-system:begin" "CLAUDE.md contains the task-system block"

BLOCK_COUNT=$(grep -c "task-system:begin" "$TARGET/CLAUDE.md" || true)
[[ "$BLOCK_COUNT" -eq 1 ]] \
    && pass "task-system block appears exactly once (count: $BLOCK_COUNT)" \
    || fail "task-system block count is $BLOCK_COUNT, expected 1"

LINK_TARGET=$(readlink "$TARGET/GEMINI.md" 2>/dev/null || echo "")
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
