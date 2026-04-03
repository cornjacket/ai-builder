#!/usr/bin/env bats
# Tests for project/tasks/scripts/task-json-helpers.sh

SCRIPTS_DIR="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../../project/tasks/scripts" && pwd)"

setup() {
    TEST_DIR="$(mktemp -d)"
    JSON_FILE="$TEST_DIR/task.json"
    cat > "$JSON_FILE" <<'EOF'
{
  "name": "test-task",
  "status": "in-progress",
  "flag": false,
  "next-subtask-id": "0002",
  "subtasks": [
    {"name": "alpha", "complete": false},
    {"name": "beta",  "complete": true}
  ]
}
EOF
    # shellcheck source=/dev/null
    source "$SCRIPTS_DIR/task-json-helpers.sh"
}

teardown() {
    rm -rf "$TEST_DIR"
}

@test "json_get: reads a string field" {
    result="$(json_get "$JSON_FILE" "name")"
    [ "$result" = "test-task" ]
}

@test "json_get: reads a boolean field as true/false string" {
    result="$(json_get "$JSON_FILE" "flag")"
    [ "$result" = "false" ]
}

@test "json_get: returns empty string for missing field" {
    result="$(json_get "$JSON_FILE" "nonexistent")"
    [ "$result" = "" ]
}

@test "json_set_str: sets a string field" {
    json_set_str "$JSON_FILE" "status" "complete"
    result="$(json_get "$JSON_FILE" "status")"
    [ "$result" = "complete" ]
}

@test "json_set_bool: sets a boolean field to true" {
    json_set_bool "$JSON_FILE" "flag" "true"
    result="$(json_get "$JSON_FILE" "flag")"
    [ "$result" = "true" ]
}

@test "json_set_bool: sets a boolean field to false" {
    json_set_bool "$JSON_FILE" "flag" "false"
    result="$(json_get "$JSON_FILE" "flag")"
    [ "$result" = "false" ]
}

@test "get_and_increment_subtask_id: returns current id and increments" {
    result="$(get_and_increment_subtask_id "$JSON_FILE")"
    [ "$result" = "0002" ]
    next="$(json_get "$JSON_FILE" "next-subtask-id")"
    [ "$next" = "0003" ]
}

@test "json_append_subtask: adds a new incomplete subtask" {
    json_append_subtask "$JSON_FILE" "gamma"
    result="$(python3 -c "import json; d=json.load(open('$JSON_FILE')); print(d['subtasks'][-1]['name'])")"
    [ "$result" = "gamma" ]
}

@test "json_complete_subtask: marks matching subtask complete" {
    json_complete_subtask "$JSON_FILE" "alpha"
    result="$(python3 -c "import json; d=json.load(open('$JSON_FILE')); print(d['subtasks'][0]['complete'])")"
    [ "$result" = "True" ]
}

@test "json_next_subtask: returns first incomplete subtask" {
    result="$(json_next_subtask "$JSON_FILE")"
    [ "$result" = "alpha" ]
}

@test "json_next_subtask: exits 1 when all subtasks are complete" {
    json_complete_subtask "$JSON_FILE" "alpha"
    run json_next_subtask "$JSON_FILE"
    [ "$status" -eq 1 ]
}

@test "json_subtasks_complete: exits 1 when subtasks are incomplete" {
    run json_subtasks_complete "$JSON_FILE"
    [ "$status" -eq 1 ]
}

@test "json_subtasks_complete: exits 0 when all subtasks are complete" {
    json_complete_subtask "$JSON_FILE" "alpha"
    run json_subtasks_complete "$JSON_FILE"
    [ "$status" -eq 0 ]
}

@test "get_parent_short_id: extracts hex prefix from dirname" {
    result="$(get_parent_short_id "/some/path/a3f2c1-my-task")"
    [ "$result" = "a3f2c1" ]
}
