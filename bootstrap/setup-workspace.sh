#!/usr/bin/env bash
# Set up the ai-builder git worktree workspace.
#
# Run from the cornjacket/ parent directory after cloning the repo into
# ai-builder-bootstrap/:
#
#   git clone <remote-url> ai-builder-bootstrap
#   bash ai-builder-bootstrap/bootstrap/setup-workspace.sh
#   rm -rf ai-builder-bootstrap
#
# Creates:
#   ai-builder/
#       .bare/     bare clone of the repo (git object store)
#       .git       file pointing to .bare/ (makes git CLI work from workspace root)
#       main/      worktree for the main branch

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOTSTRAP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PARENT_DIR="$(cd "$BOOTSTRAP_DIR/.." && pwd)"
WORKSPACE="$PARENT_DIR/ai-builder"

# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------

if [[ "$(basename "$BOOTSTRAP_DIR")" != "ai-builder-bootstrap" ]]; then
    echo "ERROR: This script must be run from ai-builder-bootstrap/."
    echo "  Expected: ai-builder-bootstrap/bootstrap/setup-workspace.sh"
    echo "  Got:      $BOOTSTRAP_DIR"
    exit 1
fi

if [[ -e "$WORKSPACE" ]]; then
    echo "ERROR: $WORKSPACE already exists."
    echo "  Remove or rename it before running this script."
    exit 1
fi

REMOTE_URL="$(git -C "$BOOTSTRAP_DIR" remote get-url origin 2>/dev/null || true)"
if [[ -z "$REMOTE_URL" ]]; then
    echo "ERROR: Could not read remote origin URL from $BOOTSTRAP_DIR."
    exit 1
fi

echo "=== Setting up ai-builder workspace ==="
echo ""
echo "  Bootstrap clone : $BOOTSTRAP_DIR"
echo "  Remote URL      : $REMOTE_URL"
echo "  Workspace       : $WORKSPACE"
echo ""

# ---------------------------------------------------------------------------
# Create workspace and bare clone
# ---------------------------------------------------------------------------

echo "[1/6] Creating workspace directory..."
mkdir -p "$WORKSPACE"

echo "[2/6] Bare-cloning from bootstrap clone (local, fast)..."
git clone --bare "$BOOTSTRAP_DIR" "$WORKSPACE/.bare"

echo "[3/6] Reconfiguring remote to point to GitHub..."
git -C "$WORKSPACE/.bare" remote set-url origin "$REMOTE_URL"
git -C "$WORKSPACE/.bare" config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"

echo "[4/6] Writing .git pointer file..."
echo "gitdir: ./.bare" > "$WORKSPACE/.git"

echo "[5/6] Adding main worktree..."
git -C "$WORKSPACE" worktree add main main

echo "[6/6] Symlinking workspace README to main/README.md..."
ln -s main/README.md "$WORKSPACE/README.md"

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

echo ""
echo "=== Workspace ready ==="
echo ""
echo "  $WORKSPACE/"
echo "  ├── .bare/     (git object store)"
echo "  ├── .git       (points to .bare/)"
echo "  └── main/      (main branch worktree)"
echo ""
echo "Next steps:"
echo "  1. Delete the bootstrap clone:"
echo "     rm -rf $BOOTSTRAP_DIR"
echo ""
echo "  2. Rename .claude/ project memory to match the new path:"
echo "     OLD: ~/.claude/projects/...cornjacket-ai-builder/"
echo "     NEW: ~/.claude/projects/...cornjacket-ai-builder-main/"
echo ""
echo "  3. Copy sandbox/ from your previous repo (if migrating):"
echo "     cp -r <previous-repo>/sandbox/. $WORKSPACE/main/sandbox/"
echo ""
echo "  4. To create a new branch worktree:"
echo "     bash $WORKSPACE/main/bootstrap/new-worktree.sh <branch-name>"
