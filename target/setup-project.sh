#!/usr/bin/env bash
# Install the ai-builder project management system into a target repository.
#
# An installed ai-builder is two stacked layers with different owners:
#
#   Layer 1 — task system   : from the PINNED create-project-system generator
#                             in vendor/create-project-system/ (see its PIN
#                             file and vendor/README.md)
#   Layer 2 — pipeline      : create-ai-builder's own hand-maintained scripts,
#                             overlaid on top of layer 1
#
# The generator never emits pipeline machinery — there is no --with-pipeline
# flag. Layer 2 is ours and stays ours.
#
# Usage:
#   setup-project.sh <target-repo-path> [--epic <name>]
#
# Options:
#   --epic <name>   Epic name for the initial directory structure (default: main)
#
# Example:
#   setup-project.sh ~/code/my-app
#   setup-project.sh ~/code/my-app --epic core

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

GENERATOR="$REPO_ROOT/vendor/create-project-system/generate.sh"
PIN_FILE="$REPO_ROOT/vendor/create-project-system/PIN"
PIPELINE_SCRIPTS_SRC="$REPO_ROOT/project/tasks/scripts"

# Layer 2 — create-ai-builder's own pipeline machinery. These are NOT produced
# by the generator; they are overlaid on top of the generated task system.
PIPELINE_SCRIPTS=(
    advance-pipeline.sh
    check-stop-after.sh
    new-pipeline-build.sh
    new-pipeline-subtask.sh
    on-task-complete.sh
    set-current-job.sh
    pipeline-build-template.md
)

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------

TARGET_REPO=""
EPIC="main"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --epic) EPIC="$2"; shift 2 ;;
        -*) echo "Unknown flag: $1"; exit 1 ;;
        *)
            if [[ -z "$TARGET_REPO" ]]; then
                TARGET_REPO="$1"
            else
                echo "Unexpected argument: $1"
                exit 1
            fi
            shift
            ;;
    esac
done

if [[ -z "$TARGET_REPO" ]]; then
    echo "Usage: setup-project.sh <target-repo-path> [--epic <name>]"
    exit 1
fi

if [[ ! -d "$TARGET_REPO" ]]; then
    echo "Target repository not found: $TARGET_REPO"
    exit 1
fi

TARGET_TASKS="$TARGET_REPO/project/tasks"

# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------

if [[ ! -x "$GENERATOR" ]]; then
    echo "Pinned task-system generator not found or not executable:"
    echo "  $GENERATOR"
    echo ""
    echo "The generator is vendored, not fetched. See vendor/README.md."
    exit 1
fi

for f in "${PIPELINE_SCRIPTS[@]}"; do
    if [[ ! -f "$PIPELINE_SCRIPTS_SRC/$f" ]]; then
        echo "Pipeline overlay source missing: $PIPELINE_SCRIPTS_SRC/$f"
        exit 1
    fi
done

# Idempotency check. NOTE: the generator itself is non-destructive and
# re-runnable (machinery overwritten, task content never touched), so this
# hard exit is more conservative than it needs to be. The install-vs-upgrade
# contract is decided in subtask 15d940-0004-define-reinstall-contract.
if [[ -d "$TARGET_TASKS" ]]; then
    echo "Project management system already installed at: $TARGET_TASKS"
    echo "Nothing to do. To reinstall, remove $TARGET_TASKS first."
    exit 0
fi

# ---------------------------------------------------------------------------
# Layer 1 — task system, from the pinned generator
# ---------------------------------------------------------------------------

echo "=== Layer 1: task system (pinned create-project-system) ==="
if [[ -f "$PIN_FILE" ]]; then
    echo "    pin: $(grep -E '^tag:' "$PIN_FILE" | awk '{print $2}') " \
         "($(grep -E '^sha:' "$PIN_FILE" | awk '{print substr($2,1,7)}'))"
fi
echo ""

# One call lands the machinery, docs/USING.md, the task-system skill, and the
# CLAUDE.md block. --with-projects and --with-worktree-guard keep the target's
# script surface at parity with what ai-builder itself uses.
"$GENERATOR" \
    --target-repo "$TARGET_REPO" \
    --tasks-dir   project/tasks \
    --epic        "$EPIC" \
    --with-status \
    --with-skill \
    --inject-claude-md \
    --with-projects \
    --with-worktree-guard

# ---------------------------------------------------------------------------
# Layer 2 — pipeline overlay (create-ai-builder's own)
# ---------------------------------------------------------------------------
#
# Seam only: the 7 pipeline scripts. Orchestrator, roles and machines are
# added by subtask 15d940-0002-pipeline-overlay-layer-2.

echo ""
echo "=== Layer 2: pipeline overlay (create-ai-builder) ==="

for f in "${PIPELINE_SCRIPTS[@]}"; do
    cp "$PIPELINE_SCRIPTS_SRC/$f" "$TARGET_TASKS/scripts/$f"
done
find "$TARGET_TASKS/scripts" -name "*.sh" -exec chmod +x {} \;

echo "  ~ project/tasks/scripts/  (pipeline: ${#PIPELINE_SCRIPTS[@]} files)"

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

echo ""
echo "Installed into: $TARGET_REPO"
echo ""
echo "Next steps:"
echo "  1. Read $TARGET_TASKS/docs/USING.md for usage instructions"
echo "  2. Create your first task:"
echo "     $TARGET_TASKS/scripts/new-user-task.sh --epic $EPIC --folder draft --name my-first-task"
