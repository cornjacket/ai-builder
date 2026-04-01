#!/usr/bin/env bash
# Run the doc pipeline against the doc-user-service source tree.
# Run reset.sh first to set up the sandbox.

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$DIR/../../.." && pwd)"

TARGET_REPO="$REPO_ROOT/sandbox/doc-user-service-target"
OUTPUT_DIR="$REPO_ROOT/sandbox/doc-user-service-output"

if [[ ! -f "$OUTPUT_DIR/current-job.txt" ]]; then
    echo "ERROR: $OUTPUT_DIR/current-job.txt not found — run reset.sh first"
    exit 1
fi

python3 "$REPO_ROOT/ai-builder/orchestrator/orchestrator.py" \
    --target-repo   "$TARGET_REPO" \
    --output-dir    "$OUTPUT_DIR" \
    --epic          main \
    --state-machine "$REPO_ROOT/ai-builder/orchestrator/machines/doc/default.json"
