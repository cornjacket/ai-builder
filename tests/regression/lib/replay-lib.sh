#!/usr/bin/env bash
# Shared replay logic for regression tests.
#
# Source this file after setting the required variables. The caller's
# test-replay.sh is responsible for setting:
#
#   Required:
#     DIR           — absolute path to the test directory (for reset.sh)
#     REPO_ROOT     — absolute path to the repo root
#     RECORD_DIR    — sandbox directory containing the recording
#     BRANCH        — recording branch name in ai-builder-recordings
#     STATE_MACHINE — path to the orchestrator state machine JSON
#     TOP_TASK_NAME — task name suffix in target repo path
#                     (e.g. "user-service", "platform")
#
#   Optional:
#     REMOTE_URL    — defaults to cornjacket/ai-builder-recordings

set -euo pipefail

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

REMOTE_URL="${REMOTE_URL:-https://github.com/cornjacket/ai-builder-recordings.git}"
TARGET_REPO="$RECORD_DIR/target"
OUTPUT_DIR="$RECORD_DIR/output"
ORCHESTRATOR="$REPO_ROOT/ai-builder/orchestrator/orchestrator.py"
COMPARE_SNAPSHOT="$REPO_ROOT/ai-builder/orchestrator/compare_snapshot.py"

PASS=0
FAIL=1

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
#
# Parse the role/outcome sequence from the replay's execution.log and compare
# against the manifest's AI invocations. Sequence match = same routing path.
# ---------------------------------------------------------------------------

_step "Verify routing path"

python3 - "$RECORD_DIR/recording.json" "$OUTPUT_DIR/execution.log" <<'PYEOF'
import json, re, sys

manifest_path, log_path = sys.argv[1], sys.argv[2]

# Recorded AI sequence from manifest
manifest = json.loads(open(manifest_path).read())
recorded = [(inv["role"], inv["outcome"]) for inv in manifest["invocations"] if inv.get("ai")]

# Replayed AI sequence from execution.log.
# Format: "[timestamp] ROLE/agent" on one line, "OUTCOME: VALUE" on the next.
# Only collect AI invocations (agent != "internal") to match the manifest filter.
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
#
# Compare the working tree against the recording's final snapshot.
# Exclude volatile files: execution.log and per-role logs.
# The Level:TOP task.json and README.md contain timestamps and token counts
# that differ between a live recording and a replay (replay is near-instant
# with zero tokens). Exclude them by their exact pinned path; all component
# subtask task.json and README.md files remain in the comparison.
# ---------------------------------------------------------------------------

_step "Verify output artifacts"

TOP_TASK_DIR="target/project/tasks/main/in-progress/${TASK_HEX_ID}-${TOP_TASK_NAME}/X-${TASK_HEX_ID}-0000-build-1"

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
