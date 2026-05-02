#!/usr/bin/env bats
# Tests for project/tasks/scripts/list-tasks.sh focused on --category
# and --group-by-category.

SCRIPTS_DIR="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../../project/tasks/scripts" && pwd)"

# Build an isolated task tree in TEST_DIR and symlink scripts into it so
# REPO_ROOT (three levels up from scripts dir) resolves to TEST_DIR.
setup() {
    TEST_DIR="$(mktemp -d)"

    for folder in draft backlog in-progress complete; do
        mkdir -p "$TEST_DIR/project/tasks/main/$folder"
    done

    mkdir -p "$TEST_DIR/project/tasks/scripts"
    ln -s "$SCRIPTS_DIR"/*.sh "$TEST_DIR/project/tasks/scripts/"
    ln -s "$SCRIPTS_DIR"/*.md "$TEST_DIR/project/tasks/scripts/" 2>/dev/null || true

    LIST="$TEST_DIR/project/tasks/scripts/list-tasks.sh"

    seed_task() {
        local name="$1" category="$2" priority="$3"
        local dir="$TEST_DIR/project/tasks/main/backlog/$name"
        mkdir -p "$dir"
        cat > "$dir/README.md" <<EOF
# Task: $name

| Field    | Value         |
|----------|---------------|
| Status   | backlog       |
| Priority | $priority     |
| Category | $category     |

## Goal
Test goal.
EOF
    }

    # Six tasks across four categories with mixed priorities.
    seed_task "aaa111-tooling-high"  "task-tooling"     "HIGH"
    seed_task "aaa222-tooling-med"   "task-tooling"     "MED"
    seed_task "bbb111-docs-high"     "docs"             "HIGH"
    seed_task "ccc111-orch-low"      "orchestrator-core" "LOW"
    seed_task "ddd111-no-cat"        "—"                "—"
    seed_task "eee111-gemini-high"   "gemini-compat"    "HIGH"

    # backlog README listing all tasks (READMEs marker drives traversal order)
    cat > "$TEST_DIR/project/tasks/main/backlog/README.md" <<'EOF'
# main / backlog

## Tasks

<!-- task-list-start -->
- [aaa111-tooling-high](aaa111-tooling-high/)
- [aaa222-tooling-med](aaa222-tooling-med/)
- [bbb111-docs-high](bbb111-docs-high/)
- [ccc111-orch-low](ccc111-orch-low/)
- [ddd111-no-cat](ddd111-no-cat/)
- [eee111-gemini-high](eee111-gemini-high/)
<!-- task-list-end -->
EOF
}

teardown() {
    rm -rf "$TEST_DIR"
}

# ---------------------------------------------------------------------------
# --category
# ---------------------------------------------------------------------------

@test "--category filters to matching tasks only" {
    run bash "$LIST" --epic main --folder backlog --category task-tooling
    [ "$status" -eq 0 ]
    [[ "$output" == *"aaa111-tooling-high"* ]]
    [[ "$output" == *"aaa222-tooling-med"* ]]
    [[ "$output" != *"bbb111-docs-high"* ]]
    [[ "$output" != *"ccc111-orch-low"* ]]
    [[ "$output" != *"eee111-gemini-high"* ]]
}

@test "--category unclassified matches Category '—' or missing field" {
    run bash "$LIST" --epic main --folder backlog --category unclassified
    [ "$status" -eq 0 ]
    [[ "$output" == *"ddd111-no-cat"* ]]
    [[ "$output" != *"aaa111-tooling-high"* ]]
}

@test "--category with unknown value yields no tasks" {
    run bash "$LIST" --epic main --folder backlog --category bogus-class
    [ "$status" -eq 0 ]
    [[ "$output" != *"aaa111-tooling-high"* ]]
    [[ "$output" != *"bbb111-docs-high"* ]]
    [[ "$output" != *"ccc111-orch-low"* ]]
    [[ "$output" != *"ddd111-no-cat"* ]]
    [[ "$output" != *"eee111-gemini-high"* ]]
}

@test "--category combined with --sort-priority orders within filter" {
    run bash "$LIST" --epic main --folder backlog --category task-tooling --sort-priority
    [ "$status" -eq 0 ]
    high_line=$(echo "$output" | grep -n "aaa111-tooling-high" | cut -d: -f1)
    med_line=$(echo "$output" | grep -n "aaa222-tooling-med" | cut -d: -f1)
    [ "$high_line" -lt "$med_line" ]
}

# ---------------------------------------------------------------------------
# --group-by-category
# ---------------------------------------------------------------------------

@test "--group-by-category prints groups in canonical class order" {
    run bash "$LIST" --epic main --folder backlog --group-by-category
    [ "$status" -eq 0 ]
    gemini_line=$(echo "$output" | grep -n "\[gemini-compat\]" | cut -d: -f1)
    orch_line=$(echo "$output" | grep -n "\[orchestrator-core\]" | cut -d: -f1)
    tooling_line=$(echo "$output" | grep -n "\[task-tooling\]" | cut -d: -f1)
    docs_line=$(echo "$output" | grep -n "\[docs\]" | cut -d: -f1)
    unclassified_line=$(echo "$output" | grep -n "\[unclassified\]" | cut -d: -f1)
    [ "$gemini_line" -lt "$orch_line" ]
    [ "$orch_line" -lt "$tooling_line" ]
    [ "$tooling_line" -lt "$docs_line" ]
    [ "$docs_line" -lt "$unclassified_line" ]
}

@test "--group-by-category puts unclassified last" {
    run bash "$LIST" --epic main --folder backlog --group-by-category
    [ "$status" -eq 0 ]
    [[ "$output" == *"[unclassified]"* ]]
    unclassified_line=$(echo "$output" | grep -n "\[unclassified\]" | cut -d: -f1)
    last_known_line=$(echo "$output" | grep -nE "\[(task-tooling|docs|workspace-mgmt)\]" | tail -1 | cut -d: -f1)
    [ "$unclassified_line" -ge "$last_known_line" ]
}

@test "--group-by-category with --sort-priority orders HIGH before MED within a group" {
    run bash "$LIST" --epic main --folder backlog --group-by-category --sort-priority
    [ "$status" -eq 0 ]
    high_line=$(echo "$output" | grep -n "aaa111-tooling-high" | cut -d: -f1)
    med_line=$(echo "$output" | grep -n "aaa222-tooling-med" | cut -d: -f1)
    [ "$high_line" -lt "$med_line" ]
}

@test "--group-by-category combined with --category yields a single group" {
    run bash "$LIST" --epic main --folder backlog --group-by-category --category task-tooling
    [ "$status" -eq 0 ]
    [[ "$output" == *"[task-tooling]"* ]]
    [[ "$output" != *"[gemini-compat]"* ]]
    [[ "$output" != *"[orchestrator-core]"* ]]
    [[ "$output" != *"[docs]"* ]]
    [[ "$output" != *"[unclassified]"* ]]
    [[ "$output" == *"aaa111-tooling-high"* ]]
    [[ "$output" == *"aaa222-tooling-med"* ]]
}

# ---------------------------------------------------------------------------
# Backwards compatibility — default behavior unchanged
# ---------------------------------------------------------------------------

@test "default invocation (no flags) lists all backlog tasks unchanged" {
    run bash "$LIST" --epic main --folder backlog
    [ "$status" -eq 0 ]
    [[ "$output" == *"aaa111-tooling-high"* ]]
    [[ "$output" == *"bbb111-docs-high"* ]]
    [[ "$output" == *"ccc111-orch-low"* ]]
    [[ "$output" == *"ddd111-no-cat"* ]]
    [[ "$output" == *"eee111-gemini-high"* ]]
    # No category sub-headings when grouping is off.
    [[ "$output" != *"[task-tooling]"* ]]
}
