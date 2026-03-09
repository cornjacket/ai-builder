#!/usr/bin/env bash
# Reset the fibonacci regression test to its initial state.
# Run this before re-running the pipeline.

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="$DIR/work"

echo "Resetting fibonacci regression test..."

# Restore the task document from the gold file
cp "$WORK/TASK-fibonacci-demo.md.gold" "$WORK/TASK-fibonacci-demo.md"

# Remove generated artifacts
rm -rf "$WORK/fibonacci"
rm -f  "$WORK/execution.log"
rm -rf "$WORK/logs"

echo "Done. Ready to run:"
echo "  python3 ai-builder/orchestrator.py \\"
echo "      --task tests/regression/fibonacci/work/TASK-fibonacci-demo.md \\"
echo "      --output-dir tests/regression/fibonacci/work"
