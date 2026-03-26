#!/usr/bin/env bash
# Run a single component test step from its gold state.
#
# Usage:
#   run.sh --step <step-name> --start-state <ROLE> [--expected-outcome <OUTCOME>]
#
# Flags:
#   --step             gold state name (must exist in steps/<step>/gold/)
#   --start-state      orchestrator start role (ARCHITECT, IMPLEMENTOR, TESTER, ...)
#   --expected-outcome if set, scan execution.log for this outcome and fail if missing
#
# What it does:
#   1. Wipes TARGET_REPO and reinstalls bare task system (scripts + CLAUDE.md only)
#   2. Overlays gold task tree (project/tasks/) onto the fresh TARGET_REPO
#   3. Wipes OUTPUT_DIR and restores gold output directory
#   4. Runs orchestrator with --start-state and --resume
#      (--resume auto-loads handoff-state.json from output dir)
#   5. Verifies expected outcome in execution.log (if --expected-outcome specified)
#
# Exit codes:
#   0 — orchestrator exited 0 and outcome verified (if checked)
#   1 — orchestrator failed or outcome check failed

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$DIR/../../../../" && pwd)"

TARGET_REPO="$REPO_ROOT/sandbox/user-service-target"
OUTPUT_DIR="$REPO_ROOT/sandbox/user-service-output"
EPIC="main"

STEP=""
START_STATE=""
EXPECTED_OUTCOME=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --step)             STEP="$2";             shift 2 ;;
        --start-state)      START_STATE="$2";      shift 2 ;;
        --expected-outcome) EXPECTED_OUTCOME="$2"; shift 2 ;;
        *) echo "Unknown flag: $1" >&2; exit 1 ;;
    esac
done

if [[ -z "$STEP" || -z "$START_STATE" ]]; then
    echo "Usage: run.sh --step <step> --start-state <ROLE> [--expected-outcome <OUTCOME>]" >&2
    exit 1
fi

GOLD_DIR="$DIR/steps/$STEP/gold"
if [[ ! -d "$GOLD_DIR" ]]; then
    echo "ERROR: Gold state not found at $GOLD_DIR" >&2
    echo "       Run capture.sh --step $STEP first." >&2
    exit 1
fi

echo "=== Component test: $STEP (start-state: $START_STATE) ==="
echo ""

# ---------------------------------------------------------------------------
# 1. Fresh target repo — scripts and CLAUDE.md only (no task tree yet)
# ---------------------------------------------------------------------------

echo "[1/4] Recreating target repo infrastructure..."
rm -rf "$TARGET_REPO"
mkdir -p "$TARGET_REPO"
"$REPO_ROOT/target/setup-project.sh" "$TARGET_REPO" --epic "$EPIC"
"$REPO_ROOT/target/init-claude-md.sh" "$TARGET_REPO"

# ---------------------------------------------------------------------------
# 2. Overlay gold task tree
# ---------------------------------------------------------------------------

echo "[2/4] Restoring gold task tree..."
cp -r "$GOLD_DIR/target-tasks/." "$TARGET_REPO/project/tasks/"

# ---------------------------------------------------------------------------
# 3. Restore gold output directory
#    current-job.txt and handoff-state.json (if any) are included here.
# ---------------------------------------------------------------------------

echo "[3/4] Restoring gold output directory..."
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"
if [[ -d "$GOLD_DIR/output" && "$(ls -A "$GOLD_DIR/output" 2>/dev/null)" ]]; then
    cp -r "$GOLD_DIR/output/." "$OUTPUT_DIR/"
fi

# ---------------------------------------------------------------------------
# 4. Run orchestrator
#    --resume: bypasses Level:TOP validation (correct for mid-pipeline starts)
#              and auto-loads handoff-state.json from OUTPUT_DIR if present
#    --start-state: overrides machine start_state
# ---------------------------------------------------------------------------

echo "[4/4] Running orchestrator..."
echo ""

python3 "$REPO_ROOT/ai-builder/orchestrator/orchestrator.py" \
    --target-repo   "$TARGET_REPO" \
    --output-dir    "$OUTPUT_DIR" \
    --epic          "$EPIC" \
    --state-machine "$REPO_ROOT/ai-builder/orchestrator/machines/default.json" \
    --start-state   "$START_STATE" \
    --resume
ORCHESTRATOR_EXIT=$?

echo ""

# ---------------------------------------------------------------------------
# Verify expected outcome (if specified)
# ---------------------------------------------------------------------------

if [[ -n "$EXPECTED_OUTCOME" ]]; then
    echo "=== Verifying outcome ==="
    LOG="$OUTPUT_DIR/execution.log"
    if [[ ! -f "$LOG" ]]; then
        echo "FAIL: execution.log not found at $LOG" >&2
        exit 1
    fi
    if grep -q "OUTCOME: $EXPECTED_OUTCOME" "$LOG"; then
        echo "PASS: OUTCOME: $EXPECTED_OUTCOME"
    else
        echo "FAIL: 'OUTCOME: $EXPECTED_OUTCOME' not found in execution.log" >&2
        echo ""
        echo "Last 20 lines of execution.log:"
        tail -20 "$LOG"
        exit 1
    fi
fi

exit $ORCHESTRATOR_EXIT
