#!/usr/bin/env bash
# Record a reference run of the doc-platform-monolith regression test.
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

RECORD_DIR="$REPO_ROOT/sandbox/regressions/doc-platform-monolith"
BRANCH="doc-platform-monolith"
DESCRIPTION="Doc pipeline — platform-monolith source tree documentation generation"
STATE_MACHINE="$REPO_ROOT/ai-builder/orchestrator/machines/doc/default.json"
FORMAT="doc"
FORCE=0

for arg in "$@"; do
    [[ "$arg" == "--force" ]] && FORCE=1
done

source "$DIR/../lib/record-lib.sh"
