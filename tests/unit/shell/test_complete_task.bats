#!/usr/bin/env bats
# Tests for project/tasks/scripts/complete-task.sh (user-task and user-subtask paths)

SCRIPTS_DIR="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../../project/tasks/scripts" && pwd)"

setup() {
    TEST_DIR="$(mktemp -d)"

    for folder in draft backlog in-progress complete; do
        mkdir -p "$TEST_DIR/project/tasks/main/$folder"
    done

    mkdir -p "$TEST_DIR/project/tasks/scripts"
    ln -s "$SCRIPTS_DIR"/*.sh "$TEST_DIR/project/tasks/scripts/"
    ln -s "$SCRIPTS_DIR"/*.md "$TEST_DIR/project/tasks/scripts/" 2>/dev/null || true

    COMPLETE="$TEST_DIR/project/tasks/scripts/complete-task.sh"

    # ---- Top-level task fixture ----
    TASK_DIR="$TEST_DIR/project/tasks/main/in-progress/abc123-top-task"
    mkdir -p "$TASK_DIR"
    cat > "$TASK_DIR/README.md" <<'EOF'
# Task: top-task

| Field     | Value       |
|-----------|-------------|
| Status    | in-progress |
| Completed | —           |

## Goal

Test top-level complete.
EOF
    cat > "$TEST_DIR/project/tasks/main/in-progress/README.md" <<'EOF'
# main / in-progress

## Tasks

<!-- task-list-start -->
- [abc123-top-task](abc123-top-task/)
<!-- task-list-end -->
EOF

    # ---- Subtask fixture ----
    PARENT_DIR="$TEST_DIR/project/tasks/main/in-progress/def456-parent-task"
    mkdir -p "$PARENT_DIR"
    cat > "$PARENT_DIR/README.md" <<'EOF'
# Task: parent-task

| Field | Value |
|-------|-------|
| Status | in-progress |

## Subtasks

<!-- subtask-list-start -->
- [ ] [def456-0000-sub-one](def456-0000-sub-one/)
<!-- subtask-list-end -->
EOF
    SUBTASK_DIR="$PARENT_DIR/def456-0000-sub-one"
    mkdir -p "$SUBTASK_DIR"
    cat > "$SUBTASK_DIR/README.md" <<'EOF'
# Task: sub-one

| Field     | Value |
|-----------|-------|
| Status    | —     |
| Completed | —     |
EOF
}

teardown() {
    rm -rf "$TEST_DIR"
}

# ---- Top-level task tests ----

@test "complete top-level task: moves to complete/" {
    run bash "$COMPLETE" --epic main --folder in-progress --name abc123-top-task
    [ "$status" -eq 0 ]
    [ -d "$TEST_DIR/project/tasks/main/complete/abc123-top-task" ]
    [ ! -d "$TEST_DIR/project/tasks/main/in-progress/abc123-top-task" ]
}

@test "complete top-level task: updates Status to complete" {
    bash "$COMPLETE" --epic main --folder in-progress --name abc123-top-task
    readme="$TEST_DIR/project/tasks/main/complete/abc123-top-task/README.md"
    grep -q "| Status.*complete" "$readme"
}

@test "complete top-level task: sets Completed date" {
    bash "$COMPLETE" --epic main --folder in-progress --name abc123-top-task
    readme="$TEST_DIR/project/tasks/main/complete/abc123-top-task/README.md"
    today="$(date +%Y-%m-%d)"
    grep -q "| Completed.*$today" "$readme"
}

@test "complete top-level task: fails when task not found" {
    run bash "$COMPLETE" --epic main --folder in-progress --name nonexistent
    [ "$status" -ne 0 ]
}

@test "complete top-level task: undo moves back to original folder" {
    bash "$COMPLETE" --epic main --folder in-progress --name abc123-top-task
    run bash "$COMPLETE" --epic main --folder in-progress --name abc123-top-task --undo
    [ "$status" -eq 0 ]
    [ -d "$TEST_DIR/project/tasks/main/in-progress/abc123-top-task" ]
    [ ! -d "$TEST_DIR/project/tasks/main/complete/abc123-top-task" ]
}

# ---- User subtask tests ----

@test "complete user subtask: renames dir to X-<name>" {
    run bash "$COMPLETE" --epic main --folder in-progress \
        --parent def456-parent-task --name def456-0000-sub-one
    [ "$status" -eq 0 ]
    [ -d "$TEST_DIR/project/tasks/main/in-progress/def456-parent-task/X-def456-0000-sub-one" ]
    [ ! -d "$TEST_DIR/project/tasks/main/in-progress/def456-parent-task/def456-0000-sub-one" ]
}

@test "complete user subtask: updates checkbox in parent README" {
    bash "$COMPLETE" --epic main --folder in-progress \
        --parent def456-parent-task --name def456-0000-sub-one
    grep -q "\- \[x\]" "$TEST_DIR/project/tasks/main/in-progress/def456-parent-task/README.md"
}

@test "complete user subtask: sets Status to complete in subtask README" {
    bash "$COMPLETE" --epic main --folder in-progress \
        --parent def456-parent-task --name def456-0000-sub-one
    readme="$TEST_DIR/project/tasks/main/in-progress/def456-parent-task/X-def456-0000-sub-one/README.md"
    grep -q "| Status.*complete" "$readme"
}
