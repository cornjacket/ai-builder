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

# ---------------------------------------------------------------------------
# Archive previous run (if any) to runs/YYYY-MM-DD-HH-MM-SS/ before clearing.
# Updates last_run symlink to the new run directory.
# ---------------------------------------------------------------------------

_save_last_run() {
    if [[ ! -f "$OUTPUT_DIR/execution.log" ]]; then
        return 0
    fi

    local ts run_dir
    ts=$(date "+%Y-%m-%d-%H-%M-%S")
    run_dir="$DIR/runs/$ts"
    mkdir -p "$run_dir"

    cp "$OUTPUT_DIR/execution.log" "$run_dir/"

    # Update last_run symlink to the new run directory
    rm -f "$DIR/last_run"
    (cd "$DIR" && ln -sf "runs/$ts" last_run)

    echo "    archived run to runs/$ts"
}

echo "=== Resetting fibonacci regression test ==="
echo ""

echo "[1/2] Clearing output dir at $OUTPUT_DIR ..."
_save_last_run
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

echo "[2/2] Resetting task.json (clearing ARCHITECT-written fields) ..."
python3 - "$DIR/task.json" <<'PYEOF'
import json, sys
path = sys.argv[1]
data = json.loads(open(path).read())
for field in ("design", "acceptance_criteria", "test_command"):
    data[field] = ""
with open(path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PYEOF

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
