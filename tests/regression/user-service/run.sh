#!/usr/bin/env bash
# Record a reference run of the user-service regression test.
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

RECORD_DIR="$REPO_ROOT/sandbox/regressions/user-service"
BRANCH="user-service"
DESCRIPTION="TM single-level decomposition — service decomposed into 3 components"
STATE_MACHINE="$REPO_ROOT/ai-builder/orchestrator/machines/builder/default.json"
FORMAT="builder"
FORCE=0

for arg in "$@"; do
    [[ "$arg" == "--force" ]] && FORCE=1
done

source "$DIR/../lib/record-lib.sh"
