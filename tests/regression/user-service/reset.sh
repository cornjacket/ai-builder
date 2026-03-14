#!/usr/bin/env bash
# Reset the user-service decomposition regression test to its initial state.
# Run this before each pipeline run.
#
# What this does:
#   1. Creates a fresh target repo at sandbox/user-service-target/
#   2. Installs the task management system and CLAUDE.md
#   3. Creates the user-service task in in-progress/ with Goal/Context populated
#   4. Points current-job.txt at the task README (simulating Oracle)
#   5. Clears any previous pipeline artifacts from the output dir

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$DIR/../../.." && pwd)"

TARGET_REPO="$REPO_ROOT/sandbox/user-service-target"
OUTPUT_DIR="$REPO_ROOT/sandbox/user-service-output"
EPIC="main"
TASK_NAME="user-service"

echo "=== Resetting user-service regression test ==="
echo ""

# ---------------------------------------------------------------------------
# 1. Fresh target repo
# ---------------------------------------------------------------------------

echo "[1/4] Creating fresh target repo at $TARGET_REPO ..."
rm -rf "$TARGET_REPO"
mkdir -p "$TARGET_REPO"

# ---------------------------------------------------------------------------
# 2. Install task management system and CLAUDE.md
# ---------------------------------------------------------------------------

echo "[2/4] Installing task management system ..."
"$REPO_ROOT/target/setup-project.sh" "$TARGET_REPO" --epic "$EPIC"
"$REPO_ROOT/target/init-claude-md.sh" "$TARGET_REPO"

SCRIPTS="$TARGET_REPO/project/tasks/scripts"

# ---------------------------------------------------------------------------
# 3. Create user-service task in in-progress/ with Goal/Context populated
# ---------------------------------------------------------------------------

echo "[3/4] Creating user-service task in in-progress/ ..."

"$SCRIPTS/new-task.sh" --epic "$EPIC" --folder in-progress --name "$TASK_NAME"

# Find the generated task directory (it gets a short hash prefix)
TASK_DIR=$(find "$TARGET_REPO/project/tasks/$EPIC/in-progress" -maxdepth 1 -type d -name "*-$TASK_NAME" | head -1)
if [[ -z "$TASK_DIR" ]]; then
    echo "ERROR: Could not find created task directory for $TASK_NAME"
    exit 1
fi
TASK_FULL_NAME="$(basename "$TASK_DIR")"

# Write the task README with Goal and Context populated.
# Components, Design, Acceptance Criteria left for ARCHITECT to fill.
cat > "$TASK_DIR/README.md" <<'TASKEOF'
# Task: user-service

| Field       | Value           |
|-------------|-----------------|
| Status      | in-progress     |
| Epic        | main            |
| Tags        | regression-test |
| Parent      | —               |
| Priority    | MED             |
| Complexity  | —               |
| Stop-after  | false           |
| Last-task   | false           |

## Goal

Build a user management HTTP service in Go with the following API:

- `POST /users` — create a user (JSON body), return the created user with generated ID
- `GET /users/{id}` — retrieve user by ID; return 404 if not found
- `PUT /users/{id}` — update user by ID; return 404 if not found
- `DELETE /users/{id}` — delete user by ID; return 404 if not found

Port: 8080. Response format: JSON. Storage: in-memory. No authentication.

## Context

This is a regression test for the ai-builder decomposition pipeline.
The pipeline must decompose this service into components, implement each
one, and verify the assembled service passes the acceptance criteria.

## Components

_To be completed by the ARCHITECT._

## Design

_To be completed by the ARCHITECT._

## Acceptance Criteria

_To be completed by the ARCHITECT._

## Suggested Tools

_To be completed by the ARCHITECT._

## Subtasks

<!-- When a subtask is finished, run complete-task.sh --parent to mark it [x] before moving on. -->
<!-- subtask-list-start -->
<!-- subtask-list-end -->

## Notes

_None._
TASKEOF

echo "    task: $TASK_FULL_NAME"

# ---------------------------------------------------------------------------
# 4. Point current-job.txt at the task README (simulating Oracle)
# ---------------------------------------------------------------------------

echo "[4/4] Pointing current-job.txt at task README ..."
mkdir -p "$OUTPUT_DIR"
rm -f  "$OUTPUT_DIR/execution.log"
rm -rf "$OUTPUT_DIR/logs"

"$SCRIPTS/set-current-job.sh" \
    --output-dir "$OUTPUT_DIR" \
    "$TASK_DIR/README.md"

echo ""
echo "=== Reset complete ==="
echo ""
echo "Target repo : $TARGET_REPO"
echo "Output dir  : $OUTPUT_DIR"
echo ""
echo "Run the pipeline:"
echo "  python3 $REPO_ROOT/ai-builder/orchestrator/orchestrator.py \\"
echo "      --target-repo $TARGET_REPO \\"
echo "      --output-dir  $OUTPUT_DIR \\"
echo "      --epic        $EPIC"
echo ""
echo "Then run the gold test:"
echo "  cd $DIR/gold && go test -tags regression ./..."
