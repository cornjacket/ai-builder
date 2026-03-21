#!/usr/bin/env bash
# Reset the platform-monolith regression test to its initial state.
# Run this before each pipeline run.
#
# What this does:
#   1. Creates a fresh target repo at sandbox/platform-monolith-target/
#   2. Installs the task management system and CLAUDE.md
#   3. Creates a USER-TASK "platform" in in-progress/ (Oracle-owned boundary)
#   4. Creates a PIPELINE-SUBTASK "build-1" under it with Level=TOP
#   5. Writes the platform spec to the build-1 README
#   6. Points current-job.txt at the build-1 README (simulating Oracle)
#   7. Clears any previous pipeline artifacts from the output dir

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$DIR/../../.." && pwd)"

TARGET_REPO="$REPO_ROOT/sandbox/platform-monolith-target"
OUTPUT_DIR="$REPO_ROOT/sandbox/platform-monolith-output"
EPIC="main"
PARENT_TASK_NAME="platform"
ENTRY_TASK_NAME="build-1"
FORCE=false

for arg in "$@"; do
    [[ "$arg" == "--force" ]] && FORCE=true
done

# ---------------------------------------------------------------------------
# Save previous run (if any) to last_run/ before wiping.
# Captures execution.log, run-metrics.json, run-summary.md, and the
# Level:TOP pipeline README from the target repo (has the execution log table).
# ---------------------------------------------------------------------------

_save_last_run() {
    if [[ ! -f "$OUTPUT_DIR/execution.log" ]]; then
        return 0
    fi
    rm -rf "$DIR/last_run"
    mkdir -p "$DIR/last_run"
    mv "$OUTPUT_DIR/execution.log" "$DIR/last_run/"
    [[ -f "$OUTPUT_DIR/run-metrics.json" ]] && mv "$OUTPUT_DIR/run-metrics.json" "$DIR/last_run/"
    [[ -f "$OUTPUT_DIR/run-summary.md"  ]] && mv "$OUTPUT_DIR/run-summary.md"   "$DIR/last_run/"
    # Find and copy the Level:TOP pipeline README (contains the execution log table).
    if [[ -f "$OUTPUT_DIR/current-job.txt" ]]; then
        local current_job search_dir level
        current_job=$(cat "$OUTPUT_DIR/current-job.txt")
        search_dir="$(dirname "$current_job")"
        while [[ "$search_dir" != "/" && "$search_dir" != "$TARGET_REPO" ]]; do
            if [[ -f "$search_dir/task.json" ]]; then
                level=$(python3 -c "import json; d=json.load(open('$search_dir/task.json')); print(d.get('level',''))" 2>/dev/null || echo "")
                if [[ "$level" == "TOP" ]]; then
                    [[ -f "$search_dir/README.md" ]] && cp "$search_dir/README.md" "$DIR/last_run/build-README.md"
                    break
                fi
            fi
            search_dir="$(dirname "$search_dir")"
        done
    fi
    echo "    saved previous run to last_run/"
}

# ---------------------------------------------------------------------------
# Guard: abort if a pipeline run is currently in progress.
#
# Checks the Level: TOP pipeline-subtask README from the previous run.
# If the path in current-job.txt still exists on disk (not yet renamed to
# X- by complete-task.sh), the pipeline has not completed and may be running.
# ---------------------------------------------------------------------------
if [[ "$FORCE" == false && -f "$OUTPUT_DIR/current-job.txt" ]]; then
    CURRENT_JOB=$(cat "$OUTPUT_DIR/current-job.txt")

    # Walk up from the current job path to find the Level: TOP task.json.
    SEARCH_DIR="$(dirname "$CURRENT_JOB")"
    LEVEL_TOP_JSON=""
    while [[ "$SEARCH_DIR" != "/" && "$SEARCH_DIR" != "$TARGET_REPO" ]]; do
        if [[ -f "$SEARCH_DIR/task.json" ]]; then
            LEVEL=$(python3 -c "import json; d=json.load(open('$SEARCH_DIR/task.json')); print(d.get('level',''))" 2>/dev/null || echo "")
            if [[ "$LEVEL" == "TOP" ]]; then
                LEVEL_TOP_JSON="$SEARCH_DIR/task.json"
                break
            fi
        fi
        SEARCH_DIR="$(dirname "$SEARCH_DIR")"
    done

    if [[ -n "$LEVEL_TOP_JSON" ]]; then
        STATUS=$(python3 -c "import json; d=json.load(open('$LEVEL_TOP_JSON')); print(d.get('status',''))" 2>/dev/null || echo "")
        if [[ "$STATUS" != "complete" ]]; then
            echo "ERROR: Pipeline is currently in progress (Status: ${STATUS:-—})."
            echo "  Level: TOP task.json: $LEVEL_TOP_JSON"
            echo ""
            echo "Wait for the pipeline to finish before resetting."
            echo "To override (only if the process is confirmed stopped): reset.sh --force"
            exit 1
        fi
    fi
fi

echo "=== Resetting platform-monolith regression test ==="
echo ""

# ---------------------------------------------------------------------------
# Save previous run before wiping.
# ---------------------------------------------------------------------------

_save_last_run

# ---------------------------------------------------------------------------
# 1. Fresh target repo
# ---------------------------------------------------------------------------

echo "[1/5] Creating fresh target repo at $TARGET_REPO ..."
rm -rf "$TARGET_REPO"
mkdir -p "$TARGET_REPO"

# ---------------------------------------------------------------------------
# 2. Install task management system and CLAUDE.md
# ---------------------------------------------------------------------------

echo "[2/5] Installing task management system ..."
"$REPO_ROOT/target/setup-project.sh" "$TARGET_REPO" --epic "$EPIC"
"$REPO_ROOT/target/init-claude-md.sh" "$TARGET_REPO"

SCRIPTS="$TARGET_REPO/project/tasks/scripts"

# ---------------------------------------------------------------------------
# 3. Create Oracle-owned parent USER-TASK "platform" in in-progress/
# ---------------------------------------------------------------------------

echo "[3/5] Creating parent user-task 'platform' in in-progress/ ..."

"$SCRIPTS/new-user-task.sh" --epic "$EPIC" --folder in-progress --name "$PARENT_TASK_NAME"

PARENT_DIR=$(find "$TARGET_REPO/project/tasks/$EPIC/in-progress" -maxdepth 1 -type d -name "*-$PARENT_TASK_NAME" | head -1)
if [[ -z "$PARENT_DIR" ]]; then
    echo "ERROR: Could not find created task directory for $PARENT_TASK_NAME"
    exit 1
fi
PARENT_FULL_NAME="$(basename "$PARENT_DIR")"
echo "    parent task: $PARENT_FULL_NAME"

# ---------------------------------------------------------------------------
# 4. Create PIPELINE-SUBTASK "build-1" under the platform task with Level=TOP
# ---------------------------------------------------------------------------

echo "[4/5] Creating pipeline entry point 'build-1' (Level=TOP) ..."

BUILD_OUTPUT=$("$SCRIPTS/new-pipeline-build.sh" \
    --epic   "$EPIC" \
    --folder in-progress \
    --parent "$PARENT_FULL_NAME" \
    --name   "$ENTRY_TASK_NAME")

ENTRY_README=$(echo "$BUILD_OUTPUT" | grep "^README:" | awk '{print $2}')
ENTRY_DIR="$(dirname "$ENTRY_README")"
ENTRY_FULL_NAME="$(basename "$ENTRY_DIR")"
echo "    entry task:  $ENTRY_FULL_NAME"

# Write the platform spec into the build-1 README.
# Complexity is left unset (—) to trigger ARCHITECT decompose mode.
# ARCHITECT and TM fill Components, Design, Acceptance Criteria.
cat > "$ENTRY_DIR/README.md" <<'TASKEOF'
<!-- This file is managed by the ai-builder pipeline. Do not hand-edit. -->
# Task: build-1

## Goal

Build a networked monolith platform in Go. A networked monolith is a single
process with a single binary entry point (`cmd/platform/main.go`). The single
process starts two HTTP listeners on separate ports — one for metrics ingestion
and one for IAM. There is exactly one `main` package and one binary.

**Metrics listener (port 8081)**

Records frontend user interaction events.

API:
- `POST /events` — record an event; body: `{"type": "click-mouse"|"submit-form", "userId": "<string>", "payload": {}}` → 201 with event object (includes generated `id`)
- `GET /events`  — list all recorded events → 200 with JSON array

**IAM listener (port 8082)**

Identity and access management. Internally composed of two logical components:
(a) user authentication and lifecycle, and (b) authorisation/RBAC.

API:
- User lifecycle:
  - `POST /users`        — register user; body: `{"username": "<string>", "password": "<string>"}` → 201 with user object (includes `id`, no password in response)
  - `GET /users/{id}`    — get user by ID → 200 or 404
  - `DELETE /users/{id}` — delete user → 200/204 or 404
- Authentication:
  - `POST /auth/login`   — authenticate; body: `{"username": "<string>", "password": "<string>"}` → 200 with token object (includes `token` field)
  - `POST /auth/logout`  — invalidate token; header: `Authorization: Bearer <token>` → 200/204
- RBAC:
  - `POST /roles`             — create role; body: `{"name": "<string>", "permissions": ["<string>"]}` → 201 with role object (includes `id`)
  - `GET /roles`              — list roles → 200 with JSON array
  - `POST /users/{id}/roles`  — assign role to user; body: `{"roleId": "<string>"}` → 200/201
  - `GET /users/{id}/roles`   — list user's roles → 200 with JSON array
  - `POST /authz/check`       — check permission; body: `{"userId": "<string>", "permission": "<string>"}` → 200 with `{"allowed": <bool>}`

## Context

This is a regression test for the ai-builder multi-level decomposition pipeline.
The platform is a networked monolith: one process, one binary, two listeners.
The IAM listener is itself internally composed of two components (auth-lifecycle
and authz-rbac). The pipeline must traverse this multi-level tree, implementing
and testing each level before walking up to integrate the next.

**Language:** Go
**Binary:** single binary — the only `main` package in the entire codebase
must be `cmd/platform/main.go`. There must be no other `main` packages.
Component-level implementations must not create their own `cmd/` directories
or standalone binaries. `cmd/platform/main.go` starts both listeners.
**Storage:** in-memory (no database required)
**Testing requirements:**
- Unit tests at each functional level (each atomic component must have unit tests)
- End-to-end acceptance tests at each integrate step:
  - INTERNAL integrate: verify the component's contract against its API;
    do not create a standalone binary — use `net/http/httptest` or similar
  - TOP integrate (this task): create `cmd/platform/main.go` as the sole
    binary entry point; start both listeners and verify all endpoints pass

## Components

_To be completed by the ARCHITECT._

## Design

_To be completed by the ARCHITECT._

## Acceptance Criteria

_To be completed by the ARCHITECT._

## Test Command

_To be completed by the ARCHITECT._

## Suggested Tools

_To be completed by the ARCHITECT._

## Notes

_None._
TASKEOF

echo "    spec written to $ENTRY_DIR/README.md"

# ---------------------------------------------------------------------------
# 5. Point current-job.txt at the build-1 README (simulating Oracle)
# ---------------------------------------------------------------------------

echo "[5/5] Pointing current-job.txt at build-1 README ..."
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

"$SCRIPTS/set-current-job.sh" \
    --output-dir "$OUTPUT_DIR" \
    "$ENTRY_README"

echo ""
echo "=== Reset complete ==="
echo ""
echo "Target repo : $TARGET_REPO"
echo "Output dir  : $OUTPUT_DIR"
echo ""
echo "Run the pipeline:"
echo "  python3 $REPO_ROOT/ai-builder/orchestrator/orchestrator.py \\"
echo "      --target-repo   $TARGET_REPO \\"
echo "      --output-dir    $OUTPUT_DIR \\"
echo "      --epic          $EPIC \\"
echo "      --state-machine $REPO_ROOT/ai-builder/orchestrator/machines/default.json"
echo ""
echo "Then run the gold test:"
echo "  cd $DIR/gold && go test -tags regression ./..."
