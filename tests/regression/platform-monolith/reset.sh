#!/usr/bin/env bash
# Reset the platform-monolith regression test to its initial state.
# Run this before each pipeline run.
#
# What this does:
#   1. Creates a fresh target repo at sandbox/regressions/platform-monolith/target/
#   2. Installs the task management system and CLAUDE.md
#   3. Creates a USER-TASK "platform" in in-progress/ (Oracle-owned boundary)
#   4. Creates a PIPELINE-SUBTASK "build-1" under it with Level=TOP
#   5. Writes the platform spec to the build-1 README
#   6. Points current-job.txt at the build-1 README (simulating Oracle)
#   7. Clears any previous pipeline artifacts from the output dir

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$DIR/../../.." && pwd)"

TARGET_REPO="$REPO_ROOT/sandbox/regressions/platform-monolith/target"
OUTPUT_DIR="$REPO_ROOT/sandbox/regressions/platform-monolith/output"
EPIC="main"
PARENT_TASK_NAME="platform"
ENTRY_TASK_NAME="build-1"
FORCE=false

for arg in "$@"; do
    [[ "$arg" == "--force" ]] && FORCE=true
done

# ---------------------------------------------------------------------------
# Archive previous run (if any) to runs/YYYY-MM-DD-HH-MM-SS/ before wiping.
# Saves execution.log, task.json (with execution_log + run_summary), and
# README.md from the Level:TOP pipeline task. Updates last_run symlink.
# Appends a summary row to runs/run-history.md.
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

    # Find the Level:TOP task.json by searching the target repo directly.
    # This handles the X- rename that happens at pipeline completion.
    local top_json
    top_json=$(python3 - "$TARGET_REPO/project/tasks" <<'PYEOF'
import json, os, sys
for root, dirs, files in os.walk(sys.argv[1]):
    for f in files:
        if f == "task.json":
            try:
                d = json.load(open(os.path.join(root, f)))
                if d.get("level") == "TOP":
                    print(os.path.join(root, f))
                    import sys as _s; _s.exit(0)
            except Exception:
                pass
PYEOF
    ) || true

    if [[ -n "$top_json" ]]; then
        cp "$top_json" "$run_dir/task.json"
        local task_readme
        task_readme="$(dirname "$top_json")/README.md"
        [[ -f "$task_readme" ]] && cp "$task_readme" "$run_dir/README.md"

        # Append a row to runs/run-history.md
        python3 - "$run_dir/task.json" "$DIR/runs/run-history.md" <<'PYEOF'
import json, os, sys
from collections import defaultdict

task_json_path, history_path = sys.argv[1], sys.argv[2]
data = json.loads(open(task_json_path).read())
rs   = data.get("run_summary") or {}
log  = data.get("execution_log", [])

# Determine run number from existing data rows
run_num = 1
if os.path.exists(history_path):
    with open(history_path) as f:
        for line in f:
            s = line.strip()
            if s.startswith("|") and not s.startswith("| Run") and not s.startswith("|---"):
                run_num += 1

# Aggregate tokens per role
roles = defaultdict(lambda: {"in": 0, "out": 0, "cached": 0})
for inv in log:
    r = inv.get("role", "")
    roles[r]["in"]     += inv.get("tokens_in", 0)
    roles[r]["out"]    += inv.get("tokens_out", 0)
    roles[r]["cached"] += inv.get("tokens_cached", 0)

def col(r):
    t = roles[r]
    return f"{t['in']:,} / {t['out']:,} / {t['cached']:,}"

# Fall back to execution_log when run_summary is absent (failed/interrupted runs)
if rs.get("elapsed_s") is not None:
    elapsed_s = int(rs["elapsed_s"])
    date = (rs.get("start") or "—")[:10]
elif log:
    from datetime import datetime
    try:
        t0 = datetime.fromisoformat(log[0]["start"])
        t1 = datetime.fromisoformat(log[-1]["end"])
        elapsed_s = int((t1 - t0).total_seconds())
        date = log[0]["start"][:10]
    except Exception:
        elapsed_s = 0
        date = "—"
else:
    elapsed_s = 0
    date = "—"
m, s = divmod(elapsed_s, 60)
elapsed = f"{m}m {s:02d}s" if m else f"{s}s"

row = f"| {run_num} | {date} | {elapsed} | {col('ARCHITECT')} | {col('IMPLEMENTOR')} | {col('TESTER')} | | |\n"

if not os.path.exists(history_path):
    with open(history_path, "w") as f:
        f.write("# Run History\n\n")
        f.write("| Run | Date | Elapsed | ARCHITECT (in/out/cached) | IMPLEMENTOR (in/out/cached) | TESTER (in/out/cached) | Gold | Notes |\n")
        f.write("|-----|------|---------|--------------------------|----------------------------|------------------------|------|-------|\n")
        f.write(row)
else:
    with open(history_path, "a") as f:
        f.write(row)

print(f"    appended run {run_num} to run-history.md")
PYEOF
    fi

    # Update last_run symlink to the new run directory
    rm -f "$DIR/last_run"
    (cd "$DIR" && ln -sf "runs/$ts" last_run)

    echo "    archived run to runs/$ts"
}

# ---------------------------------------------------------------------------
# Guard: abort if a pipeline run is currently in progress.
#
# Checks the Level: TOP pipeline-subtask README from the previous run.
# If the path in current-job.txt still exists on disk (not yet renamed to
# X- by complete-task.sh), the pipeline has not completed and may be running.
# ---------------------------------------------------------------------------
if [[ "$FORCE" == false && -f "$OUTPUT_DIR/current-job.txt" ]]; then
    CURRENT_JOB=$(cat "$OUTPUT_DIR/current-job.txt")

    # Walk up from the current job path to find the Level: TOP task.json.
    SEARCH_DIR="$(dirname "$CURRENT_JOB")"
    LEVEL_TOP_JSON=""
    while [[ "$SEARCH_DIR" != "/" && "$SEARCH_DIR" != "$TARGET_REPO" ]]; do
        if [[ -f "$SEARCH_DIR/task.json" ]]; then
            LEVEL=$(python3 -c "import json; d=json.load(open('$SEARCH_DIR/task.json')); print(d.get('level',''))" 2>/dev/null || echo "")
            if [[ "$LEVEL" == "TOP" ]]; then
                LEVEL_TOP_JSON="$SEARCH_DIR/task.json"
                break
            fi
        fi
        SEARCH_DIR="$(dirname "$SEARCH_DIR")"
    done

    if [[ -n "$LEVEL_TOP_JSON" ]]; then
        STATUS=$(python3 -c "import json; d=json.load(open('$LEVEL_TOP_JSON')); print(d.get('status',''))" 2>/dev/null || echo "")
        if [[ "$STATUS" != "complete" ]]; then
            echo "ERROR: Pipeline is currently in progress (Status: ${STATUS:-—})."
            echo "  Level: TOP task.json: $LEVEL_TOP_JSON"
            echo ""
            echo "Wait for the pipeline to finish before resetting."
            echo "To override (only if the process is confirmed stopped): reset.sh --force"
            exit 1
        fi
    fi
fi

echo "=== Resetting platform-monolith regression test ==="
echo ""

# ---------------------------------------------------------------------------
# Save previous run before wiping.
# ---------------------------------------------------------------------------

_save_last_run

# ---------------------------------------------------------------------------
# 1. Fresh target repo
# ---------------------------------------------------------------------------

echo "[1/5] Creating fresh target repo at $TARGET_REPO ..."
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
# 3. Create Oracle-owned parent USER-TASK "platform" in in-progress/
# ---------------------------------------------------------------------------

echo "[3/5] Creating parent user-task 'platform' in in-progress/ ..."

"$SCRIPTS/new-user-task.sh" --epic "$EPIC" --folder in-progress --name "$PARENT_TASK_NAME"

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
# 4. Create PIPELINE-SUBTASK "build-1" under the platform task with Level=TOP
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
