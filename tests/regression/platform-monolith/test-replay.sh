#!/usr/bin/env bash
# Replay regression test for platform-monolith.
#
# Verifies that replaying a recording produces the same AI-generated output
# artifacts as the original run, and that the orchestrator takes the same
# routing path. Fetches the recording from remote automatically if absent.
#
# Exit codes:
#   0 — test passed
#   1 — test failed

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$DIR/../../.." && pwd)"

RECORD_DIR="$REPO_ROOT/sandbox/regressions/platform-monolith"
BRANCH="platform-monolith"
STATE_MACHINE="$REPO_ROOT/ai-builder/orchestrator/machines/builder/default.json"
TOP_TASK_NAME="platform"

source "$DIR/../lib/replay-lib.sh"
