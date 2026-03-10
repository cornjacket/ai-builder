#!/usr/bin/env bash
# Reset the template-setup regression test by removing the working directory.
# Run this before re-running test.sh.

set -euo pipefail

TARGET=/tmp/ai-builder-target

if [[ -d "$TARGET" ]]; then
    rm -rf "$TARGET"
    echo "Removed: $TARGET"
else
    echo "Nothing to reset: $TARGET does not exist"
fi

echo "Ready to run:"
echo "  tests/regression/template-setup/test.sh"
