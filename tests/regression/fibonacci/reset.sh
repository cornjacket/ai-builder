#!/usr/bin/env bash
# Reset the fibonacci regression test to its initial state.
# Run this before re-running the pipeline.

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="$DIR/work"

echo "Resetting fibonacci regression test..."

# Restore the job document from the template
cp "$WORK/JOB-fibonacci-demo.md.template" "$WORK/JOB-fibonacci-demo.md"

# Remove generated artifacts
rm -rf "$WORK/fibonacci"
rm -f  "$WORK/execution.log"
rm -rf "$WORK/logs"

echo "Done. Ready to run:"
echo "  python3 ai-builder/orchestrator/orchestrator.py \\"
echo "      --job tests/regression/fibonacci/work/JOB-fibonacci-demo.md \\"
echo "      --output-dir tests/regression/fibonacci/work"
