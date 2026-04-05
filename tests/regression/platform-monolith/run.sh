#!/usr/bin/env bash
# Run the builder pipeline against the platform-monolith target repo.
# Run reset.sh first to set up the sandbox.

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$DIR/../../.." && pwd)"

TARGET_REPO="$REPO_ROOT/sandbox/regressions/platform-monolith/target"
OUTPUT_DIR="$REPO_ROOT/sandbox/regressions/platform-monolith/output"

if [[ ! -f "$OUTPUT_DIR/current-job.txt" ]]; then
    echo "ERROR: $OUTPUT_DIR/current-job.txt not found — run reset.sh first"
    exit 1
fi

JOB=$(cat "$OUTPUT_DIR/current-job.txt")

python3 "$REPO_ROOT/ai-builder/orchestrator/orchestrator.py" \
    --job           "$JOB" \
    --target-repo   "$TARGET_REPO" \
    --output-dir    "$OUTPUT_DIR" \
    --epic          main \
    --state-machine "$REPO_ROOT/ai-builder/orchestrator/machines/builder/default.json"

bash "$REPO_ROOT/tests/regression/lib/archive-run.sh" \
    --target-repo "$TARGET_REPO" \
    --output-dir  "$OUTPUT_DIR" \
    --runs-dir    "$DIR/runs" \
    --format      builder
