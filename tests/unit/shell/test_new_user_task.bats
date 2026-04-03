#!/usr/bin/env bats
# Tests for project/tasks/scripts/new-user-task.sh

SCRIPTS_DIR="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../../project/tasks/scripts" && pwd)"
SCRIPT="$SCRIPTS_DIR/new-user-task.sh"

setup() {
    TEST_DIR="$(mktemp -d)"
    # Build a minimal project/tasks/main/draft structure that new-user-task.sh expects.
    # The script resolves REPO_ROOT as three levels up from SCRIPTS_DIR, so we can't
    # redirect it to TEST_DIR. Instead, we use the actual scripts against a real epic/folder
    # that we create in a subdirectory of the live repo — but that would be destructive.
    # Instead, we use a REPO_ROOT override via symlinking the scripts into our tmp tree.

    mkdir -p "$TEST_DIR/project/tasks/main/draft"
    mkdir -p "$TEST_DIR/project/tasks/main/backlog"

    # Create a symlink tree so the script's REPO_ROOT resolves to TEST_DIR
    mkdir -p "$TEST_DIR/project/tasks/scripts"
    ln -s "$SCRIPTS_DIR"/*.sh "$TEST_DIR/project/tasks/scripts/"
    ln -s "$SCRIPTS_DIR"/*.md "$TEST_DIR/project/tasks/scripts/" 2>/dev/null || true
    PATCHED_SCRIPT="$TEST_DIR/project/tasks/scripts/new-user-task.sh"
}

teardown() {
    rm -rf "$TEST_DIR"
}

@test "creates task directory in the specified folder" {
    run bash "$PATCHED_SCRIPT" --epic main --folder draft --name my-feature
    [ "$status" -eq 0 ]
    # Should have created exactly one directory matching the pattern
    count="$(ls "$TEST_DIR/project/tasks/main/draft/" | grep -c "my-feature" || true)"
    [ "$count" -eq 1 ]
}

@test "created README.md contains the task name" {
    run bash "$PATCHED_SCRIPT" --epic main --folder draft --name check-name
    [ "$status" -eq 0 ]
    dir="$(ls "$TEST_DIR/project/tasks/main/draft/" | grep "check-name")"
    readme="$TEST_DIR/project/tasks/main/draft/$dir/README.md"
    grep -q "check-name" "$readme"
}

@test "created README.md has correct Status field" {
    run bash "$PATCHED_SCRIPT" --epic main --folder backlog --name status-test
    [ "$status" -eq 0 ]
    dir="$(ls "$TEST_DIR/project/tasks/main/backlog/" | grep "status-test")"
    readme="$TEST_DIR/project/tasks/main/backlog/$dir/README.md"
    grep -q "| Status.*backlog" "$readme"
}

@test "created README.md has correct Priority field when supplied" {
    run bash "$PATCHED_SCRIPT" --epic main --folder draft --name priority-test --priority HIGH
    [ "$status" -eq 0 ]
    dir="$(ls "$TEST_DIR/project/tasks/main/draft/" | grep "priority-test")"
    readme="$TEST_DIR/project/tasks/main/draft/$dir/README.md"
    grep -q "| Priority.*HIGH" "$readme"
}

@test "appends entry to folder README" {
    run bash "$PATCHED_SCRIPT" --epic main --folder draft --name index-test
    [ "$status" -eq 0 ]
    grep -q "index-test" "$TEST_DIR/project/tasks/main/draft/README.md"
}

@test "fails when --folder is missing" {
    run bash "$PATCHED_SCRIPT" --epic main --name no-folder
    [ "$status" -ne 0 ]
}

@test "fails when --name is missing" {
    run bash "$PATCHED_SCRIPT" --epic main --folder draft
    [ "$status" -ne 0 ]
}

@test "fails when folder directory does not exist" {
    run bash "$PATCHED_SCRIPT" --epic main --folder nonexistent --name x
    [ "$status" -ne 0 ]
}
