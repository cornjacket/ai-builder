#!/usr/bin/env bash
# Record a reference run of the user-service regression test.
#
# Runs the full pipeline with --record-to, capturing AI responses and
# workspace snapshots after every invocation. The resulting recording
# is stored at sandbox/regressions/user-service/ and pushed to the
# ai-builder-recordings remote repo on the 'user-service' orphan branch.
#
# This script makes real AI calls and incurs token cost. Run it once to
# establish a baseline recording, then use test-replay.sh for all
# subsequent regression runs.
#
# Usage:
#   bash record.sh [--force]
#
#   --force   Overwrite an existing recording without prompting.

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$DIR/../../.." && pwd)"
ORCHESTRATOR="$REPO_ROOT/ai-builder/orchestrator/orchestrator.py"

RECORD_DIR="$REPO_ROOT/sandbox/regressions/user-service"
TARGET_REPO="$RECORD_DIR/target"
OUTPUT_DIR="$RECORD_DIR/output"
STATE_MACHINE="$REPO_ROOT/ai-builder/orchestrator/machines/builder/default.json"

REMOTE_URL="https://github.com/cornjacket/ai-builder-recordings.git"
BRANCH="user-service"

FORCE=0
for arg in "$@"; do
    [[ "$arg" == "--force" ]] && FORCE=1
done

# ---------------------------------------------------------------------------
# Guard: warn if a recording already exists
# ---------------------------------------------------------------------------

if [[ -f "$RECORD_DIR/recording.json" && $FORCE -eq 0 ]]; then
    echo "A recording already exists at $RECORD_DIR/recording.json"
    echo "Re-recording will overwrite it. Pass --force to proceed."
    exit 1
fi

# ---------------------------------------------------------------------------
# Wipe any existing recording history
# ---------------------------------------------------------------------------
#
# Always start from a clean git repo so the recording branch contains exactly
# one run's worth of commits. Old recordings are never replayed once superseded
# so there is no reason to retain them. recorder.init() returns early if .git
# exists, which would otherwise append new commits on top of old ones and
# produce confusing duplicate invocation numbers in the git log.

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
# Push recording to remote
# ---------------------------------------------------------------------------

echo ""
echo "=== Pushing recording to remote ==="

git -C "$RECORD_DIR" push --force origin "$BRANCH"

echo ""
echo "=== Recording complete ==="
echo ""
echo "Recording stored at : $RECORD_DIR/recording.json"
echo "Remote branch       : $REMOTE_URL  ($BRANCH)"
echo ""
echo "Run the replay test : bash $DIR/test-replay.sh"
