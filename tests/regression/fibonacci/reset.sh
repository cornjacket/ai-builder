#!/usr/bin/env bash
# Reset the fibonacci regression test to its initial state.
# Run this before each pipeline run.
#
# What this does:
#   1. Clears previous pipeline output from sandbox/fibonacci-output/

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$DIR/../../.." && pwd)"

OUTPUT_DIR="$REPO_ROOT/sandbox/fibonacci-output"
JOB_DOC="$DIR/JOB-fibonacci-demo.md"

echo "=== Resetting fibonacci regression test ==="
echo ""

echo "[1/1] Clearing output dir at $OUTPUT_DIR ..."
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

echo ""
echo "=== Reset complete ==="
echo ""
echo "Output dir : $OUTPUT_DIR"
echo ""
echo "Run the pipeline:"
echo "  python3 $REPO_ROOT/ai-builder/orchestrator/orchestrator.py \\"
echo "      --job           $JOB_DOC \\"
echo "      --output-dir    $OUTPUT_DIR \\"
echo "      --state-machine $REPO_ROOT/ai-builder/orchestrator/machines/simple.json"
echo ""
echo "Then run the gold test:"
echo "  cd $DIR/gold && go test -tags regression -v ./..."
