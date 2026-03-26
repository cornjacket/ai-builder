#!/usr/bin/env bash
# Reset the user-service decomposition regression test to its initial state.
# Run this before each pipeline run.
#
# What this does:
#   1. Creates a fresh target repo at sandbox/user-service-target/
#   2. Installs the task management system and CLAUDE.md
#   3. Creates a USER-TASK "user-service" in in-progress/ (Oracle-owned boundary)
#   4. Creates a PIPELINE-SUBTASK "build-1" under it with Level=TOP
#   5. Writes the user-service spec to the build-1 README
#   6. Points current-job.txt at the build-1 README (simulating Oracle)
#   7. Clears any previous pipeline artifacts from the output dir

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$DIR/../../.." && pwd)"

TARGET_REPO="$REPO_ROOT/sandbox/user-service-target"
OUTPUT_DIR="$REPO_ROOT/sandbox/user-service-output"
EPIC="main"
PARENT_TASK_NAME="user-service"
ENTRY_TASK_NAME="build-1"

# ---------------------------------------------------------------------------
# Save previous run (if any) to last_run/ before wiping.
# Captures execution.log, run-metrics.json, run-summary.md, and the
# Level:TOP pipeline README from the target repo (has the execution log table).
# ---------------------------------------------------------------------------

_save_last_run() {
    if [[ ! -f "$OUTPUT_DIR/execution.log" ]]; then
        return 0
    fi
    rm -rf "$DIR/last_run"
    mkdir -p "$DIR/last_run"
    mv "$OUTPUT_DIR/execution.log" "$DIR/last_run/"
    [[ -f "$OUTPUT_DIR/run-metrics.json" ]] && mv "$OUTPUT_DIR/run-metrics.json" "$DIR/last_run/"
    [[ -f "$OUTPUT_DIR/run-summary.md"  ]] && mv "$OUTPUT_DIR/run-summary.md"   "$DIR/last_run/"
    # Find and copy the Level:TOP pipeline README (contains the execution log table).
    if [[ -f "$OUTPUT_DIR/current-job.txt" ]]; then
        local current_job search_dir level
        current_job=$(cat "$OUTPUT_DIR/current-job.txt")
        search_dir="$(dirname "$current_job")"
        while [[ "$search_dir" != "/" && "$search_dir" != "$TARGET_REPO" ]]; do
            if [[ -f "$search_dir/task.json" ]]; then
                level=$(python3 -c "import json; d=json.load(open('$search_dir/task.json')); print(d.get('level',''))" 2>/dev/null || echo "")
                if [[ "$level" == "TOP" ]]; then
                    [[ -f "$search_dir/README.md" ]] && cp "$search_dir/README.md" "$DIR/last_run/build-README.md"
                    break
                fi
            fi
            search_dir="$(dirname "$search_dir")"
        done
    fi
    echo "    saved previous run to last_run/"
}

echo "=== Resetting user-service regression test ==="
echo ""

# ---------------------------------------------------------------------------
# 1. Fresh target repo
# ---------------------------------------------------------------------------

echo "[1/5] Creating fresh target repo at $TARGET_REPO ..."
_save_last_run
rm -rf "$TARGET_REPO"
mkdir -p "$TARGET_REPO"

# ---------------------------------------------------------------------------
# 2. Install task management system and CLAUDE.md
# ---------------------------------------------------------------------------

echo "[2/5] Installing task management system ..."
"$REPO_ROOT/target/setup-project.sh" "$TARGET_REPO" --epic "$EPIC"
"$REPO_ROOT/target/init-claude-md.sh" "$TARGET_REPO"

SCRIPTS="$TARGET_REPO/project/tasks/scripts"

# ---------------------------------------------------------------------------
# 3. Create Oracle-owned parent USER-TASK "user-service" in in-progress/
# ---------------------------------------------------------------------------

echo "[3/5] Creating parent user-task 'user-service' in in-progress/ ..."

"$SCRIPTS/new-user-task.sh" --epic "$EPIC" --folder in-progress --name "$PARENT_TASK_NAME"

PARENT_DIR=$(find "$TARGET_REPO/project/tasks/$EPIC/in-progress" -maxdepth 1 -type d -name "*-$PARENT_TASK_NAME" | head -1)
if [[ -z "$PARENT_DIR" ]]; then
    echo "ERROR: Could not find created task directory for $PARENT_TASK_NAME"
    exit 1
fi
PARENT_FULL_NAME="$(basename "$PARENT_DIR")"
echo "    parent task: $PARENT_FULL_NAME"

# ---------------------------------------------------------------------------
# 4. Create PIPELINE-SUBTASK "build-1" under the user-service task with Level=TOP
# ---------------------------------------------------------------------------

echo "[4/5] Creating pipeline entry point 'build-1' (Level=TOP) ..."

BUILD_OUTPUT=$("$SCRIPTS/new-pipeline-build.sh" \
    --epic   "$EPIC" \
    --folder in-progress \
    --parent "$PARENT_FULL_NAME" \
    --name   "$ENTRY_TASK_NAME")

ENTRY_README=$(echo "$BUILD_OUTPUT" | grep "^README:" | awk '{print $2}')
ENTRY_DIR="$(dirname "$ENTRY_README")"
ENTRY_FULL_NAME="$(basename "$ENTRY_DIR")"
echo "    entry task:  $ENTRY_FULL_NAME"

# Copy the spec into the build-1 README.
# The spec lives in tests/regression/user-service/build-spec.md so it is
# version-controlled and not regenerated from a heredoc on every reset.
# Complexity is left unset (—) to trigger ARCHITECT decompose mode.
cp "$DIR/build-spec.md" "$ENTRY_README"
echo "    spec written to $ENTRY_README"

# Backfill goal/context into task.json.
# new-pipeline-build.sh runs before the spec is written, so task.json has
# empty goal/context at that point. Extract them from the spec now.
ENTRY_TASK_JSON="$(dirname "$ENTRY_README")/task.json"
python3 - "$ENTRY_README" "$ENTRY_TASK_JSON" <<'PYEOF'
import sys, json, re
readme_path, task_json_path = sys.argv[1], sys.argv[2]
readme = open(readme_path).read()
data = json.loads(open(task_json_path).read())
for field, label in (("goal", "Goal"), ("context", "Context")):
    m = re.search(rf'## {label}\s*\n+(.*?)(?=\n## |\Z)', readme, re.DOTALL)
    if m:
        text = m.group(1).strip()
        if text and text != "_To be written._":
            data[field] = text
with open(task_json_path, 'w') as f:
    json.dump(data, f, indent=2); f.write('\n')
PYEOF
echo "    task.json updated with goal/context"

# ---------------------------------------------------------------------------
# 5. Point current-job.txt at the build-1 README (simulating Oracle)
# ---------------------------------------------------------------------------

echo "[5/5] Pointing current-job.txt at build-1 README ..."
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

"$SCRIPTS/set-current-job.sh" \
    --output-dir "$OUTPUT_DIR" \
    "$ENTRY_README"

echo ""
echo "=== Reset complete ==="
echo ""
echo "Target repo : $TARGET_REPO"
echo "Output dir  : $OUTPUT_DIR"
echo ""
echo "Run the pipeline:"
echo "  python3 $REPO_ROOT/ai-builder/orchestrator/orchestrator.py \\"
echo "      --target-repo   $TARGET_REPO \\"
echo "      --output-dir    $OUTPUT_DIR \\"
echo "      --epic          $EPIC \\"
echo "      --state-machine $REPO_ROOT/ai-builder/orchestrator/machines/default.json"
echo ""
echo "Then run the gold test:"
echo "  cd $DIR/gold && go test -tags regression ./..."
