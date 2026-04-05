#!/usr/bin/env bash
# Add a new row to the Regression tests table in the ai-builder-recordings
# main branch README.md.
#
# Run this once when pushing a regression's recording to ai-builder-recordings
# for the first time. Re-recording an existing test does not require a README
# update.
#
# Usage:
#   bash tests/regression/lib/add-to-recordings-readme.sh \
#       --name        <test-name> \
#       --description "<one-line description of what the test exercises>"
#
# Example:
#   bash tests/regression/lib/add-to-recordings-readme.sh \
#       --name        platform-monolith \
#       --description "TM two-level decomposition — IAM + metrics services in one monolith"

set -euo pipefail

REMOTE_URL="${REMOTE_URL:-https://github.com/cornjacket/ai-builder-recordings.git}"
NAME=""
DESCRIPTION=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --name)        NAME="$2";        shift 2 ;;
        --description) DESCRIPTION="$2"; shift 2 ;;
        *) echo "Unknown argument: $1"; exit 1 ;;
    esac
done

if [[ -z "$NAME" || -z "$DESCRIPTION" ]]; then
    echo "Usage: $0 --name <test-name> --description <description>"
    exit 1
fi

LINK="https://github.com/cornjacket/ai-builder-recordings/commits/${NAME}/"
NEW_ROW="| ${NAME} | [${NAME}](${LINK}) | ${DESCRIPTION} |"

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

echo "Cloning ai-builder-recordings (main) ..."
git clone --depth 1 --branch main "$REMOTE_URL" "$TMPDIR/repo" 2>&1 | grep -v "^$"

README="$TMPDIR/repo/README.md"

# No-op if already present (idempotent — safe to call on every run)
if grep -qF "| ${NAME} |" "$README"; then
    echo "'${NAME}' already in the table — nothing to do."
    exit 0
fi

# Append the new row after the last existing table data row.
# The table header always ends with '|----|' lines; data rows start with '| '.
# We find the last '| ' line inside the Regression tests section and append after it.
python3 - "$README" "$NEW_ROW" <<'PYEOF'
import sys, re

readme_path = sys.argv[1]
new_row = sys.argv[2]

with open(readme_path) as f:
    content = f.read()

# Find the Regression tests table and append the new row after the last data row.
# Strategy: locate the table header, then find the last pipe-starting line in
# the same block and insert after it.
table_header = "| Test | Commits | What it exercises |"
if table_header not in content:
    print(f"ERROR: could not find Regression tests table in README", file=sys.stderr)
    sys.exit(1)

lines = content.splitlines(keepends=True)
header_idx = next(i for i, l in enumerate(lines) if table_header in l)

# Find the last table row (starts with '|') after the header
last_row_idx = header_idx
for i in range(header_idx, len(lines)):
    if lines[i].startswith("|"):
        last_row_idx = i
    elif last_row_idx > header_idx:
        # First non-pipe line after we've seen data rows — table ended
        break

lines.insert(last_row_idx + 1, new_row + "\n")

with open(readme_path, "w") as f:
    f.writelines(lines)

print(f"Added row: {new_row}")
PYEOF

cd "$TMPDIR/repo"
git add README.md
git commit -m "Add ${NAME} to regression tests table"
git push origin main

echo ""
echo "README.md updated on main branch of ai-builder-recordings."
echo "  Added: ${NAME}"
