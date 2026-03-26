#!/usr/bin/env bash
# Capture the current sandbox state as a gold snapshot for a component test step.
#
# Usage:
#   capture.sh --step <step-name>
#
# What it captures:
#   steps/<step>/gold/target-tasks/   — project/tasks/ tree from TARGET_REPO
#   steps/<step>/gold/output/         — OUTPUT_DIR contents (code, logs, current-job.txt)
#   steps/<step>/gold/handoff-state.json — pipeline handoff state (if present)
#
# Run this at the desired checkpoint after the pipeline has reached that state.
# The captured gold directory is used by run.sh to restore sandbox state for
# single-step testing.
#
# Bootstrapping note:
#   Gold states must be captured in order, each building on the previous.
#   See README.md for the full bootstrapping procedure.

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$DIR/../../../../" && pwd)"

TARGET_REPO="$REPO_ROOT/sandbox/user-service-target"
OUTPUT_DIR="$REPO_ROOT/sandbox/user-service-output"

STEP=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --step) STEP="$2"; shift 2 ;;
        *) echo "Unknown flag: $1" >&2; exit 1 ;;
    esac
done

if [[ -z "$STEP" ]]; then
    echo "Usage: capture.sh --step <step-name>" >&2
    echo ""
    echo "Steps (in bootstrapping order):"
    echo "  01-initial           — after reset.sh, before any orchestrator run"
    echo "  02-after-decompose   — after ARCHITECT+DECOMPOSE_HANDLER, before component-1"
    echo "  03-after-component-1 — after component-1 (store) fully built"
    echo "  04-after-component-2 — after component-2 (handlers) fully built"
    echo "  05-after-component-3 — after component-3 (integrate) fully built"
    exit 1
fi

GOLD_DIR="$DIR/steps/$STEP/gold"

if [[ ! -d "$TARGET_REPO" ]]; then
    echo "ERROR: Target repo not found at $TARGET_REPO" >&2
    echo "       Run tests/regression/user-service/reset.sh first." >&2
    exit 1
fi

echo "=== Capturing gold state: $STEP ==="
echo ""

rm -rf "$GOLD_DIR"
mkdir -p "$GOLD_DIR"

# ---------------------------------------------------------------------------
# 1. Capture task tree (project/tasks/ only — scripts and CLAUDE.md are
#    reinstalled fresh by run.sh via setup-project.sh and init-claude-md.sh)
# ---------------------------------------------------------------------------

echo "  [1/3] Capturing task tree..."
mkdir -p "$GOLD_DIR/target-tasks"
cp -r "$TARGET_REPO/project/tasks/." "$GOLD_DIR/target-tasks/"

# ---------------------------------------------------------------------------
# 2. Capture output directory
#    Includes: current-job.txt, handoff-state.json, generated code, logs
# ---------------------------------------------------------------------------

echo "  [2/3] Capturing output directory..."
mkdir -p "$GOLD_DIR/output"
if [[ -d "$OUTPUT_DIR" ]]; then
    cp -r "$OUTPUT_DIR/." "$GOLD_DIR/output/"
fi

# ---------------------------------------------------------------------------
# 3. Copy handoff-state.json to gold root as a convenience alias
#    (run.sh can find it quickly without scanning output/)
# ---------------------------------------------------------------------------

if [[ -f "$OUTPUT_DIR/handoff-state.json" ]]; then
    echo "  [3/3] Copying handoff-state.json..."
    cp "$OUTPUT_DIR/handoff-state.json" "$GOLD_DIR/handoff-state.json"
else
    echo "  [3/3] No handoff-state.json (step starts from empty state — OK for step 01)."
fi

echo ""
echo "=== Captured: $GOLD_DIR ==="
echo ""
echo "File count by type:"
echo "  Task tree:  $(find "$GOLD_DIR/target-tasks" -type f | wc -l | tr -d ' ') files"
echo "  Output dir: $(find "$GOLD_DIR/output" -type f 2>/dev/null | wc -l | tr -d ' ') files"
echo ""
echo "Next: see README.md for what to do before running the next step."
