#!/usr/bin/env bash
# Replay regression test for platform-monolith.
#
# Verifies that replaying a recording produces the same AI-generated output
# artifacts as the original run, and that the orchestrator takes the same
# routing path.
#
# If no local recording exists, fetches it from the remote repo automatically.
#
# What this does:
#   1. Ensures a recording is available (fetches from remote if not present locally)
#   2. Resets the workspace (wipes output/ and target/)
#   3. Replays the recording with --replay-from (no AI calls)
#   4. Verifies the routing path matches (same role/outcome sequence)
#   5. Verifies output artifacts match the recording's final snapshot
#      (excludes volatile files: execution.log, logs/)
#
# Exit codes:
#   0 — test passed
#   1 — test failed

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$DIR/../../.." && pwd)"
ORCHESTRATOR="$REPO_ROOT/ai-builder/orchestrator/orchestrator.py"
COMPARE_SNAPSHOT="$REPO_ROOT/ai-builder/orchestrator/compare_snapshot.py"

RECORD_DIR="$REPO_ROOT/sandbox/regressions/platform-monolith"
TARGET_REPO="$RECORD_DIR/target"
OUTPUT_DIR="$RECORD_DIR/output"
STATE_MACHINE="$REPO_ROOT/ai-builder/orchestrator/machines/builder/default.json"

REMOTE_URL="https://github.com/cornjacket/ai-builder-recordings.git"
BRANCH="platform-monolith"

PASS=0
FAIL=1

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_pass() { echo "[PASS] $*"; }
_fail() { echo "[FAIL] $*" >&2; exit $FAIL; }
_step() { echo ""; echo "--- $* ---"; }

# ---------------------------------------------------------------------------
# 1. Ensure recording is available (fetch from remote if absent locally)
# ---------------------------------------------------------------------------

_step "Check recording"

if [[ ! -f "$RECORD_DIR/recording.json" ]]; then
    echo "No local recording found. Fetching from remote..."
    if [[ ! -d "$RECORD_DIR/.git" ]]; then
        git clone --branch "$BRANCH" --single-branch "$REMOTE_URL" "$RECORD_DIR"
    else
        git -C "$RECORD_DIR" fetch origin "$BRANCH"
        git -C "$RECORD_DIR" checkout "$BRANCH"
    fi
    if [[ ! -f "$RECORD_DIR/recording.json" ]]; then
        echo "error: recording.json not found after fetch — remote branch '$BRANCH' may be empty." >&2
        echo "Run record.sh to create the first recording." >&2
        exit $FAIL
    fi
    _pass "Recording fetched from remote"
else
    _pass "Recording found locally"
fi

LAST_N=$(python3 - "$RECORD_DIR/recording.json" <<'PYEOF'
import json, sys
m = json.loads(open(sys.argv[1]).read())
invs = m.get("invocations", [])
print(max(inv["n"] for inv in invs) if invs else 0)
PYEOF
)

AI_COUNT=$(python3 - "$RECORD_DIR/recording.json" <<'PYEOF'
import json, sys
m = json.loads(open(sys.argv[1]).read())
print(sum(1 for inv in m.get("invocations", []) if inv.get("ai")))
PYEOF
)

TASK_HEX_ID=$(python3 - "$RECORD_DIR/recording.json" <<'PYEOF'
import json, sys
m = json.loads(open(sys.argv[1]).read())
print(m.get("task_hex_id", ""))
PYEOF
)

_pass "Recording found (last invocation: $LAST_N, AI invocations: $AI_COUNT)"
[[ -n "$TASK_HEX_ID" ]] && echo "    task hex ID: $TASK_HEX_ID (pinned)"

# ---------------------------------------------------------------------------
# 2. Reset workspace
# ---------------------------------------------------------------------------

_step "Reset workspace"

if [[ -n "$TASK_HEX_ID" ]]; then
    bash "$DIR/reset.sh" --task-id "$TASK_HEX_ID"
else
    bash "$DIR/reset.sh"
fi

_pass "Workspace reset"

# ---------------------------------------------------------------------------
# 3. Replay
# ---------------------------------------------------------------------------

_step "Replay"

JOB_README="$(cat "$OUTPUT_DIR/current-job.txt")"

python3 "$ORCHESTRATOR" \
    --job           "$JOB_README" \
    --target-repo   "$TARGET_REPO" \
    --output-dir    "$OUTPUT_DIR" \
    --epic          main \
    --state-machine "$STATE_MACHINE" \
    --replay-from   "$RECORD_DIR"

_pass "Replay completed (exit 0)"

# ---------------------------------------------------------------------------
# 4. Verify routing path matches
# ---------------------------------------------------------------------------

_step "Verify routing path"

python3 - "$RECORD_DIR/recording.json" "$OUTPUT_DIR/execution.log" <<'PYEOF'
import json, re, sys

manifest_path, log_path = sys.argv[1], sys.argv[2]

manifest = json.loads(open(manifest_path).read())
recorded = [(inv["role"], inv["outcome"]) for inv in manifest["invocations"] if inv.get("ai")]

replayed = []
header_pat = re.compile(r'^\[.*?\] ([A-Z_]+)/(\S+)')
outcome_pat = re.compile(r'^OUTCOME:\s+(\S+)')
pending_role = None
pending_ai = False
for line in open(log_path):
    line = line.rstrip()
    m = header_pat.match(line)
    if m:
        pending_role = m.group(1)
        pending_ai = (m.group(2) != "internal")
        continue
    if pending_role is not None:
        m = outcome_pat.match(line)
        if m and pending_ai:
            replayed.append((pending_role, m.group(1)))
        pending_role = None
        pending_ai = False

if recorded != replayed:
    print(f"ROUTING MISMATCH")
    print(f"  recorded:  {recorded}")
    print(f"  replayed:  {replayed}")
    sys.exit(1)

print(f"[PASS] Routing matches ({len(replayed)} AI invocation(s))")
PYEOF

# ---------------------------------------------------------------------------
# 5. Verify output artifacts match recording snapshot
# ---------------------------------------------------------------------------

_step "Verify output artifacts"

TOP_TASK_DIR="target/project/tasks/main/in-progress/${TASK_HEX_ID}-platform/X-${TASK_HEX_ID}-0000-build-1"

python3 "$COMPARE_SNAPSHOT" \
    --recording "$RECORD_DIR" \
    --at        "$LAST_N" \
    --exclude   "output/execution.log" \
    --exclude   "output/logs" \
    --exclude   "output/current-job.txt" \
    --exclude   "output/last-job.json" \
    --exclude   "output/handoff-state.json" \
    --exclude   "responses" \
    --exclude   "recording.json" \
    --exclude   "${TOP_TASK_DIR}/task.json" \
    --exclude   "${TOP_TASK_DIR}/README.md" \
    && _pass "Output artifacts match recording snapshot" \
    || _fail "Output artifacts differ from recording snapshot (see diff above)"

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

echo ""
echo "=== Replay regression test PASSED ==="
