#!/usr/bin/env bash
# Shared recording logic for regression tests.
#
# Source this file after setting the required variables. The caller's
# run.sh is responsible for argument parsing and setting:
#
#   Required:
#     DIR           — absolute path to the test directory (for reset.sh)
#     REPO_ROOT     — absolute path to the repo root
#     RECORD_DIR    — sandbox directory for recording output
#     BRANCH        — recording branch name in ai-builder-recordings
#     DESCRIPTION   — one-line description of what this regression exercises
#     STATE_MACHINE — path to the orchestrator state machine JSON
#     FORMAT        — builder or doc (passed to archive-run.sh and run-history.md)
#     FORCE         — 0 (default) or 1 (set by --force flag)
#
#   Optional:
#     REMOTE_URL  — defaults to cornjacket/ai-builder-recordings

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

REMOTE_URL="${REMOTE_URL:-https://github.com/cornjacket/ai-builder-recordings.git}"
TARGET_REPO="$RECORD_DIR/target"
OUTPUT_DIR="$RECORD_DIR/output"
ORCHESTRATOR="$REPO_ROOT/ai-builder/orchestrator/orchestrator.py"

# ---------------------------------------------------------------------------
# Guard: warn if a recording already exists
# ---------------------------------------------------------------------------

if [[ -f "$RECORD_DIR/recording.json" && "${FORCE:-0}" -eq 0 ]]; then
    echo "A recording already exists at $RECORD_DIR/recording.json"
    echo "Re-recording will overwrite it. Pass --force to proceed."
    exit 1
fi

# ---------------------------------------------------------------------------
# Wipe any existing recording history
#
# Always start from a clean git repo so the recording branch contains exactly
# one run's worth of commits. Old recordings are never replayed once superseded
# so there is no reason to retain them. recorder.init() returns early if .git
# exists, which would otherwise append new commits on top of old ones and
# produce confusing duplicate invocation numbers in the git log.
# ---------------------------------------------------------------------------

rm -rf "$RECORD_DIR/.git"

# ---------------------------------------------------------------------------
# Reset workspace
# ---------------------------------------------------------------------------

echo "=== Resetting workspace for recording ==="
bash "$DIR/reset.sh"

# ---------------------------------------------------------------------------
# Run pipeline with --record-to
# ---------------------------------------------------------------------------

echo ""
echo "=== Recording pipeline run ==="
echo "    record dir: $RECORD_DIR"
echo "    branch:     $BRANCH"
echo "    remote:     $REMOTE_URL"
echo ""

JOB_README="$(cat "$OUTPUT_DIR/current-job.txt")"

python3 "$ORCHESTRATOR" \
    --job           "$JOB_README" \
    --target-repo   "$TARGET_REPO" \
    --output-dir    "$OUTPUT_DIR" \
    --epic          main \
    --state-machine "$STATE_MACHINE" \
    --record-to     "$RECORD_DIR" \
    --record-branch "$BRANCH" \
    --record-remote "$REMOTE_URL"

# ---------------------------------------------------------------------------
# Archive run immediately (eliminates one-run lag)
# ---------------------------------------------------------------------------

echo ""
echo "=== Archiving recording run ==="

bash "$REPO_ROOT/tests/regression/lib/archive-run.sh" \
    --target-repo "$TARGET_REPO" \
    --output-dir  "$OUTPUT_DIR" \
    --runs-dir    "$DIR/runs" \
    --format      "$FORMAT"

# ---------------------------------------------------------------------------
# Run gold tests — recording is only pushed if they pass
# ---------------------------------------------------------------------------

echo ""
echo "=== Running gold tests ==="
echo ""

if ! cd "$DIR/gold" && go test -tags regression ./...; then
    echo ""
    echo "ERROR: Gold tests failed — recording NOT pushed to remote."
    echo "Fix the issue and re-run with: bash $DIR/run.sh --force"
    exit 1
fi

cd "$REPO_ROOT"

# ---------------------------------------------------------------------------
# Push recording to remote
#
# Delete the remote branch first so the push creates a clean orphan with no
# prior history. --force alone would replace the tip but leaves old commits
# reachable via reflog; deletion + push guarantees a truly fresh branch.
# The || true handles the first recording where the branch does not exist yet.
# ---------------------------------------------------------------------------

echo ""
echo "=== Pushing recording to remote ==="

git -C "$RECORD_DIR" push origin --delete "$BRANCH" 2>/dev/null || true
git -C "$RECORD_DIR" push origin "$BRANCH"

# ---------------------------------------------------------------------------
# Update ai-builder-recordings README (idempotent — no-op if already present)
# ---------------------------------------------------------------------------

echo ""
echo "=== Updating ai-builder-recordings README ==="

bash "$REPO_ROOT/tests/regression/lib/add-to-recordings-readme.sh" \
    --name        "$BRANCH" \
    --description "${DESCRIPTION:-$BRANCH regression}"

echo ""
echo "=== Recording complete ==="
echo ""
echo "Recording stored at : $RECORD_DIR/recording.json"
echo "Remote branch       : $REMOTE_URL  ($BRANCH)"
echo ""
echo "Next steps:"
echo "  1. Fill in Gold/Notes on the new run-history row:"
echo "       bash tests/regression/lib/update-run-history.sh \\"
echo "           --history $DIR/runs/run-history.md \\"
echo "           --gold    pass \\"
echo "           --notes   \"<triggering-task>\""
echo "  2. Commit run-history.md"
echo "  3. Run the replay test to verify: bash $DIR/test-replay.sh"
