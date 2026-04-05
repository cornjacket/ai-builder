#!/usr/bin/env bash
# Archive the completed pipeline run from the sandbox to a timestamped runs/ directory.
#
# Copies execution.log, task.json, and README.md from the Level:TOP pipeline task,
# appends a summary row to run-history.md, and updates the last_run symlink.
# Safe to call immediately after the orchestrator exits — no workspace wipe.
#
# Usage:
#   archive-run.sh --target-repo <path> --output-dir <path> \
#                  --runs-dir <path> --format builder|doc
#
# If no execution.log is present in output-dir, the script exits 0 silently
# (nothing to archive).
#
# Caller variables (all required):
#   --target-repo   path to the sandbox target repo (where task.json lives)
#   --output-dir    path to the orchestrator output dir (execution.log lives here)
#   --runs-dir      path to the regression's runs/ directory
#   --format        builder (ARCHITECT/IMPLEMENTOR/TESTER) or doc (ARCHITECT/IMPLEMENTOR)

set -euo pipefail

TARGET_REPO=""
OUTPUT_DIR=""
RUNS_DIR=""
FORMAT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --target-repo) TARGET_REPO="$2"; shift 2 ;;
        --output-dir)  OUTPUT_DIR="$2";  shift 2 ;;
        --runs-dir)    RUNS_DIR="$2";    shift 2 ;;
        --format)      FORMAT="$2";      shift 2 ;;
        *) echo "Unknown argument: $1" >&2; exit 1 ;;
    esac
done

if [[ -z "$TARGET_REPO" || -z "$OUTPUT_DIR" || -z "$RUNS_DIR" || -z "$FORMAT" ]]; then
    echo "Usage: $0 --target-repo <path> --output-dir <path> --runs-dir <path> --format builder|doc" >&2
    exit 1
fi

if [[ "$FORMAT" != "builder" && "$FORMAT" != "doc" ]]; then
    echo "Error: --format must be 'builder' or 'doc'" >&2
    exit 1
fi

# Nothing to archive if the orchestrator hasn't run yet
if [[ ! -f "$OUTPUT_DIR/execution.log" ]]; then
    exit 0
fi

# ---------------------------------------------------------------------------
# Create timestamped archive directory
# ---------------------------------------------------------------------------

ts=$(date "+%Y-%m-%d-%H-%M-%S")
run_dir="$RUNS_DIR/$ts"
mkdir -p "$run_dir"

cp "$OUTPUT_DIR/execution.log" "$run_dir/"

# ---------------------------------------------------------------------------
# Find the Level:TOP task.json in the target repo
# ---------------------------------------------------------------------------

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
    task_readme="$(dirname "$top_json")/README.md"
    [[ -f "$task_readme" ]] && cp "$task_readme" "$run_dir/README.md"

    # -------------------------------------------------------------------------
    # Append a summary row to run-history.md
    # -------------------------------------------------------------------------

    python3 - "$run_dir/task.json" "$RUNS_DIR/run-history.md" "$FORMAT" <<'PYEOF'
import json, os, sys
from collections import defaultdict

task_json_path, history_path, fmt = sys.argv[1], sys.argv[2], sys.argv[3]
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

if fmt == "builder":
    row    = f"| {run_num} | {date} | {elapsed} | {col('ARCHITECT')} | {col('IMPLEMENTOR')} | {col('TESTER')} | | |\n"
    header = "| Run | Date | Elapsed | ARCHITECT (in/out/cached) | IMPLEMENTOR (in/out/cached) | TESTER (in/out/cached) | Gold | Notes |\n"
    sep    = "|-----|------|---------|--------------------------|----------------------------|------------------------|------|-------|\n"
else:  # doc
    row    = f"| {run_num} | {date} | {elapsed} | {col('ARCHITECT')} | {col('IMPLEMENTOR')} | | |\n"
    header = "| Run | Date | Elapsed | ARCHITECT (in/out/cached) | IMPLEMENTOR (in/out/cached) | Gold | Notes |\n"
    sep    = "|-----|------|---------|--------------------------|------------|------|-------|\n"

if not os.path.exists(history_path):
    with open(history_path, "w") as f:
        f.write("# Run History\n\n")
        f.write(header)
        f.write(sep)
        f.write(row)
else:
    with open(history_path, "a") as f:
        f.write(row)

print(f"    appended run {run_num} to run-history.md")
PYEOF
fi

# ---------------------------------------------------------------------------
# Update last_run symlink in the test directory (parent of runs/)
# ---------------------------------------------------------------------------

test_dir="$(dirname "$RUNS_DIR")"
rm -f "$test_dir/last_run"
(cd "$test_dir" && ln -sf "runs/$ts" last_run)

echo "    archived run to runs/$ts"
