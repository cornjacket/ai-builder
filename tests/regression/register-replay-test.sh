#!/usr/bin/env bash
# Register a new replay regression test in the ai-builder-recordings README.
#
# Adds a row to the regression table in the 'main' branch of
# cornjacket/ai-builder-recordings. Run this once after taking the first
# recording for a new test and confirming test-replay.sh passes.
#
# The script validates that the recording branch exists on the remote before
# adding the row, and fails with a clear message if not.
#
# Usage:
#   bash tests/regression/register-replay-test.sh \
#       --test <name> \
#       --description "<text>"
#
#   --test         Name of the regression test (must match the recording branch
#                  name and the directory under tests/regression/).
#                  Example: user-service
#
#   --description  One-line description of what the test exercises.
#                  Example: "TM single-level decomposition — service into 3 components"
#
# Example:
#   bash tests/regression/register-replay-test.sh \
#       --test platform-monolith \
#       --description "TM multi-level decomposition — 2-service monolith, 3-level tree"

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$DIR/../.." && pwd)"

REMOTE_URL="https://github.com/cornjacket/ai-builder-recordings.git"
WORK_DIR="/tmp/ai-builder-recordings-main-$$"

TEST_NAME=""
DESCRIPTION=""

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------

while [[ $# -gt 0 ]]; do
    case "$1" in
        --test)        TEST_NAME="$2";    shift 2 ;;
        --description) DESCRIPTION="$2"; shift 2 ;;
        *) echo "Unknown argument: $1" >&2; exit 1 ;;
    esac
done

if [[ -z "$TEST_NAME" || -z "$DESCRIPTION" ]]; then
    echo "Usage: $0 --test <name> --description <text>" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Validate: recording branch must exist on remote
# ---------------------------------------------------------------------------

echo "=== Checking remote for branch '$TEST_NAME' ==="

if ! git ls-remote --exit-code "$REMOTE_URL" "refs/heads/$TEST_NAME" > /dev/null 2>&1; then
    echo ""
    echo "error: branch '$TEST_NAME' not found on $REMOTE_URL" >&2
    echo ""
    echo "Run record.sh first to create the recording, then register it:" >&2
    echo "  bash tests/regression/$TEST_NAME/record.sh" >&2
    echo "  bash tests/regression/$TEST_NAME/test-replay.sh" >&2
    echo "  bash tests/regression/register-replay-test.sh --test $TEST_NAME --description \"...\"" >&2
    exit 1
fi

echo "  [OK] branch '$TEST_NAME' exists on remote"

# ---------------------------------------------------------------------------
# Validate: test not already registered
# ---------------------------------------------------------------------------

EXISTING=$(git ls-remote "$REMOTE_URL" "refs/heads/main" | awk '{print $1}')
CURRENT_README=$(git archive --remote="$REMOTE_URL" main README.md 2>/dev/null | tar -xO README.md 2>/dev/null || true)

if echo "$CURRENT_README" | grep -q "| $TEST_NAME |"; then
    echo ""
    echo "error: '$TEST_NAME' is already registered in the recordings README." >&2
    echo "Nothing to do." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Clone main branch and add the row
# ---------------------------------------------------------------------------

echo ""
echo "=== Cloning recordings main branch ==="

git clone --branch main --single-branch "$REMOTE_URL" "$WORK_DIR" 2>&1
trap "rm -rf '$WORK_DIR'" EXIT

echo ""
echo "=== Adding '$TEST_NAME' to README ==="

LINK="https://github.com/cornjacket/ai-builder-recordings/commits/${TEST_NAME}/"

# Insert new row into the regression table. The table ends with a blank line
# after the last | row. We find the last table row and append after it.
python3 - "$WORK_DIR/README.md" "$TEST_NAME" "$LINK" "$DESCRIPTION" << 'PYEOF'
import sys
path, name, link, desc = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
content = open(path).read()
new_row = f"| {name} | [{name}]({link}) | {desc} |"
# Find the last line that looks like a table row and insert after it
lines = content.splitlines(keepends=True)
last_table_idx = None
for i, line in enumerate(lines):
    if line.startswith("| ") and " | " in line:
        last_table_idx = i
if last_table_idx is None:
    print("error: could not find regression table in README", file=sys.stderr)
    sys.exit(1)
lines.insert(last_table_idx + 1, new_row + "\n")
open(path, "w").write("".join(lines))
print(f"  added row: {new_row}")
PYEOF

# ---------------------------------------------------------------------------
# Commit and push
# ---------------------------------------------------------------------------

echo ""
echo "=== Pushing README update to main ==="

git -C "$WORK_DIR" config user.email "recorder@ai-builder"
git -C "$WORK_DIR" config user.name "ai-builder recorder"
git -C "$WORK_DIR" add README.md
git -C "$WORK_DIR" commit -m "register replay regression test: $TEST_NAME"
git -C "$WORK_DIR" push origin main

echo ""
echo "=== Done ==="
echo ""
echo "Registered : $TEST_NAME"
echo "Description: $DESCRIPTION"
echo "Remote     : $REMOTE_URL (main)"
echo ""
echo "Next steps:"
echo "  Commit and push this registration:"
echo "    git add tests/regression/register-replay-test.sh"
echo "    git commit -m \"register $TEST_NAME replay regression\""
