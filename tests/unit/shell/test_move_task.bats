#!/usr/bin/env bats
# Tests for project/tasks/scripts/move-task.sh

SCRIPTS_DIR="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../../project/tasks/scripts" && pwd)"

# Build an isolated task tree in TEST_DIR and symlink scripts into it so
# REPO_ROOT resolves correctly (REPO_ROOT = three levels up from scripts dir).
setup() {
    TEST_DIR="$(mktemp -d)"

    for folder in draft backlog in-progress complete; do
        mkdir -p "$TEST_DIR/project/tasks/main/$folder"
    done

    mkdir -p "$TEST_DIR/project/tasks/scripts"
    ln -s "$SCRIPTS_DIR"/*.sh "$TEST_DIR/project/tasks/scripts/"
    ln -s "$SCRIPTS_DIR"/*.md "$TEST_DIR/project/tasks/scripts/" 2>/dev/null || true

    MOVE="$TEST_DIR/project/tasks/scripts/move-task.sh"

    # Seed a task in backlog
    TASK_DIR="$TEST_DIR/project/tasks/main/backlog/abc123-my-task"
    mkdir -p "$TASK_DIR"
    cat > "$TASK_DIR/README.md" <<'EOF'
# Task: my-task

| Field  | Value   |
|--------|---------|
| Status | backlog |

## Goal

Test goal.
EOF

    # Seed the backlog README with the task entry
    cat > "$TEST_DIR/project/tasks/main/backlog/README.md" <<'EOF'
# main / backlog

## Tasks

<!-- task-list-start -->
- [abc123-my-task](abc123-my-task/)
<!-- task-list-end -->
EOF
}

teardown() {
    rm -rf "$TEST_DIR"
}

@test "moves task directory to destination folder" {
    run bash "$MOVE" --epic main --name abc123-my-task --from backlog --to in-progress
    [ "$status" -eq 0 ]
    [ -d "$TEST_DIR/project/tasks/main/in-progress/abc123-my-task" ]
    [ ! -d "$TEST_DIR/project/tasks/main/backlog/abc123-my-task" ]
}

@test "updates Status field in task README" {
    run bash "$MOVE" --epic main --name abc123-my-task --from backlog --to in-progress
    readme="$TEST_DIR/project/tasks/main/in-progress/abc123-my-task/README.md"
    grep -q "| Status.*in-progress" "$readme"
}

@test "removes task entry from source README" {
    run bash "$MOVE" --epic main --name abc123-my-task --from backlog --to in-progress
    [ "$status" -eq 0 ]
    run grep "abc123-my-task" "$TEST_DIR/project/tasks/main/backlog/README.md"
    [ "$status" -ne 0 ]
}

@test "adds task entry to destination README" {
    run bash "$MOVE" --epic main --name abc123-my-task --from backlog --to in-progress
    [ "$status" -eq 0 ]
    grep -q "abc123-my-task" "$TEST_DIR/project/tasks/main/in-progress/README.md"
}

@test "fails when source task does not exist" {
    run bash "$MOVE" --epic main --name nonexistent-task --from backlog --to in-progress
    [ "$status" -ne 0 ]
}

@test "fails when task already exists at destination" {
    # Create a duplicate at destination
    mkdir -p "$TEST_DIR/project/tasks/main/in-progress/abc123-my-task"
    run bash "$MOVE" --epic main --name abc123-my-task --from backlog --to in-progress
    [ "$status" -ne 0 ]
}

@test "fails when required flags are missing" {
    run bash "$MOVE" --epic main --name abc123-my-task --from backlog
    [ "$status" -ne 0 ]
}
