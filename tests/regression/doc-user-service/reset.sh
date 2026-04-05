#!/usr/bin/env bash
# Reset the doc-user-service regression test to its initial state.
# Run this before each doc pipeline run.
#
# What this does:
#   1. Copies the source-only template to sandbox/regressions/doc-user-service/output/
#      (removes any previously generated .md files from prior runs)
#   2. Creates a fresh target repo at sandbox/regressions/doc-user-service/target/
#   3. Installs the task management system and CLAUDE.md
#   4. Creates a USER-TASK "doc-user-service" in in-progress/
#   5. Creates a PIPELINE-SUBTASK "doc-1" under it with Level=TOP
#   6. Writes the doc spec into the build README
#   7. Points current-job.txt at the doc-1 README

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$DIR/../../.." && pwd)"

SOURCE_TEMPLATE="$DIR/source"
TARGET_REPO="$REPO_ROOT/sandbox/regressions/doc-user-service/target"
OUTPUT_DIR="$REPO_ROOT/sandbox/regressions/doc-user-service/output"
EPIC="main"
PARENT_TASK_NAME="doc-user-service"
ENTRY_TASK_NAME="doc-1"
TASK_ID=""  # optional pinned hex ID (--task-id HEX); empty = generate randomly

while [[ $# -gt 0 ]]; do
    case "$1" in
        --task-id) TASK_ID="$2"; shift 2 ;;
        *) echo "Unknown argument: $1"; exit 1 ;;
    esac
done

echo "=== Resetting doc-user-service regression test ==="
echo ""

# ---------------------------------------------------------------------------
# Archive previous run (if any) before wiping.
# ---------------------------------------------------------------------------

bash "$REPO_ROOT/tests/regression/lib/archive-run.sh" \
    --target-repo "$TARGET_REPO" \
    --output-dir  "$OUTPUT_DIR" \
    --runs-dir    "$DIR/runs" \
    --format      doc

# ---------------------------------------------------------------------------
# 1. Copy source template to output dir (strips any existing .md files)
# ---------------------------------------------------------------------------

echo "[1/5] Copying source template to $OUTPUT_DIR ..."
rm -rf "$OUTPUT_DIR"
cp -r "$SOURCE_TEMPLATE" "$OUTPUT_DIR"

# Sanity check: no .md files should be in the template
if find "$OUTPUT_DIR" -name "*.md" | grep -q .; then
    echo "ERROR: .md files found in source template — remove them before committing"
    find "$OUTPUT_DIR" -name "*.md"
    exit 1
fi
echo "    source files copied (no .md files present)"

# ---------------------------------------------------------------------------
# 2. Fresh target repo
# ---------------------------------------------------------------------------

echo "[2/5] Creating fresh target repo at $TARGET_REPO ..."
rm -rf "$TARGET_REPO"
mkdir -p "$TARGET_REPO"

# ---------------------------------------------------------------------------
# 3. Install task management system and CLAUDE.md
# ---------------------------------------------------------------------------

echo "[3/5] Installing task management system ..."
"$REPO_ROOT/target/setup-project.sh" "$TARGET_REPO" --epic "$EPIC"
"$REPO_ROOT/target/init-claude-md.sh" "$TARGET_REPO"

SCRIPTS="$TARGET_REPO/project/tasks/scripts"

# ---------------------------------------------------------------------------
# 4. Create USER-TASK "doc-user-service" in in-progress/
# ---------------------------------------------------------------------------

echo "[4/5] Creating parent user-task '$PARENT_TASK_NAME' in in-progress/ ..."

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

# Write Goal and Context into the parent USER-TASK README
python3 - "$DIR/doc-spec.md" "$PARENT_DIR/README.md" <<'PYEOF'
import sys, re
spec   = open(sys.argv[1]).read()
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
# 5. Create PIPELINE-SUBTASK "doc-1" with Level=TOP
# ---------------------------------------------------------------------------

echo "[5/5] Creating pipeline entry point '$ENTRY_TASK_NAME' (Level=TOP) ..."

BUILD_OUTPUT=$("$SCRIPTS/new-pipeline-build.sh" \
    --epic   "$EPIC" \
    --folder in-progress \
    --parent "$PARENT_FULL_NAME" \
    --name   "$ENTRY_TASK_NAME")

ENTRY_README=$(echo "$BUILD_OUTPUT" | grep "^README:" | awk '{print $2}')
ENTRY_DIR="$(dirname "$ENTRY_README")"
ENTRY_FULL_NAME="$(basename "$ENTRY_DIR")"
echo "    entry task: $ENTRY_FULL_NAME"

# Copy Goal/Context from doc-spec into the pipeline entry point README too
python3 - "$DIR/doc-spec.md" "$ENTRY_README" <<'PYEOF'
import sys, re
spec   = open(sys.argv[1]).read()
readme = open(sys.argv[2]).read()
for field in ("Goal", "Context"):
    m = re.search(rf'## {field}\s*\n(.*?)(?=\n## |\Z)', spec, re.DOTALL)
    if m:
        new_section = f"## {field}\n{m.group(1)}"
        readme = re.sub(rf'## {field}\s*\n.*?(?=\n## |\Z)', new_section, readme, flags=re.DOTALL)
open(sys.argv[2], 'w').write(readme)
PYEOF

# Point current-job.txt at the doc-1 README
"$SCRIPTS/set-current-job.sh" \
    --output-dir "$OUTPUT_DIR" \
    "$ENTRY_README"

echo ""
echo "=== Reset complete ==="
echo ""
echo "Source dir  : $OUTPUT_DIR"
echo "Target repo : $TARGET_REPO"
echo ""
echo "Run the pipeline:"
echo "  bash $DIR/run.sh"
echo ""
echo "Then run the gold test:"
echo "  cd $DIR/gold && go test -tags regression ./..."
