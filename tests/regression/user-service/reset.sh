#!/usr/bin/env bash
# Reset the user-service decomposition regression test to its initial state.
# Run this before each pipeline run.
#
# What this does:
#   1. Creates a fresh target repo at sandbox/regressions/user-service/target/
#   2. Installs the task management system and CLAUDE.md
#   3. Creates a USER-TASK "user-service" in in-progress/ (Oracle-owned boundary)
#   4. Creates a PIPELINE-SUBTASK "build-1" under it with Level=TOP
#   5. Writes the user-service spec to the build-1 README
#   6. Points current-job.txt at the build-1 README (simulating Oracle)
#   7. Clears any previous pipeline artifacts from the output dir

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$DIR/../../.." && pwd)"

TARGET_REPO="$REPO_ROOT/sandbox/regressions/user-service/target"
OUTPUT_DIR="$REPO_ROOT/sandbox/regressions/user-service/output"
EPIC="main"
PARENT_TASK_NAME="user-service"
ENTRY_TASK_NAME="build-1"
TASK_ID=""  # optional pinned hex ID (--task-id HEX); empty = generate randomly

while [[ $# -gt 0 ]]; do
    case "$1" in
        --task-id) TASK_ID="$2"; shift 2 ;;
        *) echo "Unknown flag: $1"; exit 1 ;;
    esac
done

echo "=== Resetting user-service regression test ==="
echo ""

# ---------------------------------------------------------------------------
# 1. Fresh target repo — archive previous run first
# ---------------------------------------------------------------------------

echo "[1/5] Creating fresh target repo at $TARGET_REPO ..."
bash "$REPO_ROOT/tests/regression/lib/archive-run.sh" \
    --target-repo "$TARGET_REPO" \
    --output-dir  "$OUTPUT_DIR" \
    --runs-dir    "$DIR/runs" \
    --format      builder
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

if [[ -n "$TASK_ID" ]]; then
    "$SCRIPTS/new-user-task.sh" --epic "$EPIC" --folder in-progress --name "$PARENT_TASK_NAME" --id "$TASK_ID"
else
    "$SCRIPTS/new-user-task.sh" --epic "$EPIC" --folder in-progress --name "$PARENT_TASK_NAME"
fi

PARENT_DIR=$(find "$TARGET_REPO/project/tasks/$EPIC/in-progress" -maxdepth 1 -type d -name "*-$PARENT_TASK_NAME" | head -1)
if [[ -z "$PARENT_DIR" ]]; then
    echo "ERROR: Could not find created task directory for $PARENT_TASK_NAME"
    exit 1
fi
PARENT_FULL_NAME="$(basename "$PARENT_DIR")"
echo "    parent task: $PARENT_FULL_NAME"

# Write Goal and Context from build-spec.md into the parent USER-TASK README.
# Preserves the metadata table (Next-subtask-id etc.) created by new-user-task.sh.
# new-pipeline-build.sh reads goal/context from here to populate task.json.
python3 - "$DIR/build-spec.md" "$PARENT_DIR/README.md" <<'PYEOF'
import sys, re
spec  = open(sys.argv[1]).read()
readme = open(sys.argv[2]).read()
for field in ("Goal", "Context"):
    m = re.search(rf'## {field}\s*\n(.*?)(?=\n## |\Z)', spec, re.DOTALL)
    if m:
        new_section = f"## {field}\n{m.group(1)}"
        readme = re.sub(rf'## {field}\s*\n.*?(?=\n## |\Z)', new_section, readme, flags=re.DOTALL)
open(sys.argv[2], 'w').write(readme)
PYEOF
echo "    spec written to $PARENT_DIR/README.md"

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
echo "      --state-machine $REPO_ROOT/ai-builder/orchestrator/machines/builder/default.json"
echo ""
echo "Then run the gold test:"
echo "  cd $DIR/gold && go test -tags regression ./..."
